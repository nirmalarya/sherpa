#!/bin/sh
# Session 144 - Quick Verification Script

echo "🏔️  SHERPA V1 - Session 144 Verification"
echo "========================================="
echo ""

# Check backend
echo "1. Checking backend (port 8001)..."
if lsof -i :8001 | grep LISTEN > /dev/null; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is NOT running"
fi

# Check frontend
echo "2. Checking frontend (port 3003)..."
if lsof -i :3003 | grep LISTEN > /dev/null; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend is NOT running"
fi

# Check database
echo "3. Checking database..."
if [ -f "sherpa/data/sherpa.db" ]; then
    echo "   ✅ Database file exists"
else
    echo "   ❌ Database file NOT found"
fi

# Check frontend build
echo "4. Checking frontend files..."
if [ -d "sherpa/frontend/src" ]; then
    echo "   ✅ Frontend source files exist"
else
    echo "   ❌ Frontend source NOT found"
fi

# Check feature list
echo "5. Checking feature_list.json..."
if [ -f "feature_list.json" ]; then
    PASSING=$(grep -c '"passes": true' feature_list.json)
    FAILING=$(grep -c '"passes": false' feature_list.json)
    echo "   ✅ Feature list exists: $PASSING passing, $FAILING failing"
else
    echo "   ❌ Feature list NOT found"
fi

echo ""
echo "========================================="
echo "Verification complete!"
echo ""
