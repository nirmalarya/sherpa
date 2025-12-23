#!/bin/bash
# Docker Compose Test Script for SHERPA V1
# Tests all 6 steps from feature_list.json

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=6
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP $1/6]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((PASSED_TESTS++))
}

print_error() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((FAILED_TESTS++))
}

print_info() {
    echo -e "${YELLOW}ℹ INFO:${NC} $1"
}

# Cleanup function
cleanup() {
    echo ""
    echo "=================================================="
    echo "Cleaning up..."
    echo "=================================================="
    docker-compose down -v 2>/dev/null || true
    echo "Cleanup complete"
}

# Trap errors and cleanup
trap cleanup EXIT

echo "=================================================="
echo "Docker Compose Test Suite for SHERPA V1"
echo "=================================================="
echo ""

# Step 1: Run docker-compose up
print_step 1 "Run docker-compose up"
print_info "Building and starting all services..."

if docker-compose build --quiet 2>&1; then
    print_success "Docker Compose build completed"
else
    print_error "Docker Compose build failed"
    exit 1
fi

if docker-compose up -d 2>&1; then
    print_success "Docker Compose services started"
else
    print_error "Docker Compose up failed"
    exit 1
fi

echo ""
sleep 5

# Step 2: Verify backend container starts
print_step 2 "Verify backend container starts"
print_info "Checking backend container status..."

if docker-compose ps | grep -q "sherpa-backend.*Up"; then
    print_success "Backend container is running"

    # Check backend logs
    print_info "Backend container logs (last 5 lines):"
    docker-compose logs --tail=5 backend
else
    print_error "Backend container is not running"
    docker-compose ps
    docker-compose logs backend
fi

echo ""
sleep 3

# Step 3: Verify frontend container starts
print_step 3 "Verify frontend container starts"
print_info "Checking frontend container status..."

if docker-compose ps | grep -q "sherpa-frontend.*Up"; then
    print_success "Frontend container is running"

    # Check frontend logs
    print_info "Frontend container logs (last 5 lines):"
    docker-compose logs --tail=5 frontend
else
    print_error "Frontend container is not running"
    docker-compose ps
    docker-compose logs frontend
fi

echo ""
sleep 3

# Step 4: Verify database container starts
print_step 4 "Verify database container starts"
print_info "Checking database container status..."

if docker-compose ps | grep -q "sherpa-db.*Up"; then
    print_success "Database container is running"

    # Check database logs
    print_info "Database container logs (last 5 lines):"
    docker-compose logs --tail=5 db
else
    print_error "Database container is not running"
    docker-compose ps
    docker-compose logs db
fi

echo ""
sleep 2

# Step 5: Verify containers can communicate
print_step 5 "Verify containers can communicate"
print_info "Testing network connectivity between containers..."

# Test backend can reach database
if docker-compose exec -T backend ping -c 1 db >/dev/null 2>&1; then
    print_success "Backend can communicate with database"
else
    print_error "Backend cannot communicate with database"
fi

# Test frontend can reach backend
if docker-compose exec -T frontend ping -c 1 backend >/dev/null 2>&1; then
    print_success "Frontend can communicate with backend"
else
    print_error "Frontend cannot communicate with backend"
fi

# Test backend health endpoint from host
print_info "Testing backend health endpoint from host..."
sleep 5  # Wait for services to fully start

if wget --spider --quiet --tries=3 --timeout=10 http://localhost:8000/health; then
    print_success "Backend health endpoint accessible from host"
else
    print_error "Backend health endpoint not accessible from host"
    print_info "Attempting to get more information..."
    docker-compose logs --tail=20 backend
fi

# Test frontend from host
print_info "Testing frontend from host..."
if wget --spider --quiet --tries=3 --timeout=10 http://localhost:3001; then
    print_success "Frontend accessible from host"
else
    print_error "Frontend not accessible from host"
    print_info "Attempting to get more information..."
    docker-compose logs --tail=20 frontend
fi

echo ""

# Step 6: Verify volumes mounted correctly
print_step 6 "Verify volumes mounted correctly"
print_info "Checking volume mounts..."

# Check backend data volume
if docker-compose exec -T backend ls -la /app/sherpa/data >/dev/null 2>&1; then
    print_success "Backend data volume mounted correctly"
else
    print_error "Backend data volume not mounted correctly"
fi

# Check backend logs volume
if docker-compose exec -T backend ls -la /app/sherpa/logs >/dev/null 2>&1; then
    print_success "Backend logs volume mounted correctly"
else
    print_error "Backend logs volume not mounted correctly"
fi

# Check backend snippets.local volume
if docker-compose exec -T backend ls -la /app/sherpa/snippets.local >/dev/null 2>&1; then
    print_success "Backend snippets.local volume mounted correctly"
else
    print_error "Backend snippets.local volume not mounted correctly"
fi

# Check database volume
if docker volume inspect sherpa_db-data >/dev/null 2>&1; then
    print_success "Database volume exists"
else
    print_error "Database volume not created"
fi

echo ""

# Summary
echo "=================================================="
echo "Test Summary"
echo "=================================================="
echo -e "Total Tests: ${BLUE}${TOTAL_TESTS}${NC}"
echo -e "Passed: ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed: ${RED}${FAILED_TESTS}${NC}"
echo ""

# Show running containers
echo "Running Containers:"
docker-compose ps

echo ""
echo "Network Information:"
docker network ls | grep sherpa || echo "No sherpa networks found"

echo ""
echo "Volume Information:"
docker volume ls | grep sherpa || echo "No sherpa volumes found"

echo ""
echo "=================================================="
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo "Docker Compose setup is working correctly!"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo "Please review the errors above and fix the issues."
    exit 1
fi
