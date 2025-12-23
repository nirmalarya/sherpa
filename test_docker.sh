#!/bin/bash

# SHERPA V1 - Docker Testing Script
# Comprehensive verification of Docker deployment

set -e

echo "=========================================="
echo "SHERPA V1 - Docker Deployment Test"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test tracking
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((TESTS_FAILED++))
}

info() {
    echo -e "${YELLOW}ℹ INFO${NC}: $1"
}

# Cleanup function
cleanup() {
    info "Cleaning up test containers..."
    docker rm -f sherpa-test-1 sherpa-test-2 sherpa-test-3 2>/dev/null || true
}

# Set cleanup trap
trap cleanup EXIT

echo "Step 1: Build Docker Image"
echo "----------------------------------------"
if docker build -t sherpa-backend:latest . > /tmp/sherpa-docker-build.log 2>&1; then
    pass "Docker image built successfully"
    IMAGE_SIZE=$(docker images sherpa-backend:latest --format "{{.Size}}")
    info "Image size: $IMAGE_SIZE"
else
    fail "Docker image build failed"
    cat /tmp/sherpa-docker-build.log
    exit 1
fi
echo ""

echo "Step 2: Verify Image Exists"
echo "----------------------------------------"
if docker images | grep -q "sherpa-backend.*latest"; then
    pass "Image sherpa-backend:latest exists"
    docker images | grep "sherpa-backend"
else
    fail "Image not found in docker images"
    exit 1
fi
echo ""

echo "Step 3: Run Container (Basic)"
echo "----------------------------------------"
if docker run -d --name sherpa-test-1 -p 8888:8000 sherpa-backend:latest > /tmp/sherpa-container-id.txt; then
    CONTAINER_ID=$(cat /tmp/sherpa-container-id.txt)
    pass "Container started successfully"
    info "Container ID: ${CONTAINER_ID:0:12}"
else
    fail "Container failed to start"
    exit 1
fi

# Wait for container to start
info "Waiting for application to start (5 seconds)..."
sleep 5
echo ""

echo "Step 4: Verify Application Starts"
echo "----------------------------------------"
LOGS=$(docker logs sherpa-test-1 2>&1)
if echo "$LOGS" | grep -q "Uvicorn running"; then
    pass "Application started successfully"
    echo "$LOGS" | grep "Uvicorn running"
else
    fail "Application did not start properly"
    echo "$LOGS"
    exit 1
fi
echo ""

echo "Step 5: Verify API Accessible from Host"
echo "----------------------------------------"
if curl -s http://localhost:8888/health > /tmp/sherpa-health-response.json; then
    if grep -q "healthy" /tmp/sherpa-health-response.json; then
        pass "API is accessible and healthy"
        cat /tmp/sherpa-health-response.json | python3 -m json.tool 2>/dev/null || cat /tmp/sherpa-health-response.json
    else
        fail "API returned unexpected response"
        cat /tmp/sherpa-health-response.json
    fi
else
    fail "Cannot connect to API"
    docker logs sherpa-test-1
    exit 1
fi
echo ""

echo "Step 6: Verify Environment Variables"
echo "----------------------------------------"
# Test with staging environment
info "Starting container with SHERPA_ENV=staging..."
if docker run -d --name sherpa-test-2 -p 8889:8000 -e SHERPA_ENV=staging sherpa-backend:latest; then
    sleep 5

    if curl -s http://localhost:8889/api/environment > /tmp/sherpa-env-response.json; then
        if grep -q "staging" /tmp/sherpa-env-response.json; then
            pass "Environment variable SHERPA_ENV=staging works correctly"
            cat /tmp/sherpa-env-response.json | python3 -m json.tool 2>/dev/null || cat /tmp/sherpa-env-response.json
        else
            fail "Environment not set to staging"
            cat /tmp/sherpa-env-response.json
        fi
    else
        fail "Cannot access environment endpoint"
    fi
else
    fail "Container with env vars failed to start"
fi
echo ""

echo "Step 7: Verify Health Check"
echo "----------------------------------------"
info "Waiting for health check to run (35 seconds)..."
sleep 35

HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' sherpa-test-1 2>/dev/null || echo "unknown")
if [ "$HEALTH_STATUS" = "healthy" ]; then
    pass "Container health check is healthy"
else
    fail "Container health check failed (status: $HEALTH_STATUS)"
    docker inspect sherpa-test-1 | grep -A 10 "Health"
fi
echo ""

echo "Step 8: Verify Container Logs"
echo "----------------------------------------"
FULL_LOGS=$(docker logs sherpa-test-1 2>&1)
if echo "$FULL_LOGS" | grep -q "Application startup complete"; then
    pass "Application startup completed successfully"
else
    fail "Application startup not confirmed in logs"
    echo "$FULL_LOGS"
fi
echo ""

echo "Step 9: Verify Port Mapping"
echo "----------------------------------------"
PORT_MAPPING=$(docker port sherpa-test-1)
if echo "$PORT_MAPPING" | grep -q "8000/tcp -> 0.0.0.0:8888"; then
    pass "Port mapping correct (8888 -> 8000)"
    echo "$PORT_MAPPING"
else
    fail "Port mapping incorrect"
    echo "$PORT_MAPPING"
fi
echo ""

echo "Step 10: Test Multiple API Endpoints"
echo "----------------------------------------"
# Test metrics endpoint
if curl -s http://localhost:8888/metrics > /dev/null; then
    pass "Metrics endpoint accessible"
else
    fail "Metrics endpoint not accessible"
fi

# Test API version endpoint
if curl -s http://localhost:8888/api/v1/health > /dev/null; then
    pass "API versioning endpoint accessible"
else
    fail "API versioning endpoint not accessible"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo ""
    echo "Docker deployment is working correctly!"
    echo ""
    echo "To run the container in production:"
    echo "  docker run -d --name sherpa -p 8000:8000 sherpa-backend:latest"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the errors above."
    echo ""
    exit 1
fi
