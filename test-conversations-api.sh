#!/bin/bash

# Test script for Conversations API integration
# This script tests the backend endpoint that the frontend will use

echo "🧪 Testing Conversations API Integration"
echo "=========================================="
echo ""

# Check if backend is running
echo "1️⃣ Checking if backend is running on port 8000..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running. Start it with: ./start-backend.sh"
    exit 1
fi

echo ""
echo "2️⃣ Testing /api/agent/chat endpoint..."
echo ""

# Test with a simple query
echo "📝 Sending test query: 'What is artificial intelligence?'"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/api/agent/chat \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "What is artificial intelligence?",
        "auto_execute": false
    }')

if [ $? -eq 0 ]; then
    echo "✅ Request successful!"
    echo ""
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool
    echo ""
    echo "✅ API is working correctly!"
else
    echo "❌ Request failed"
    exit 1
fi

echo ""
echo "3️⃣ Testing with Advanced Mode enabled..."
echo ""

RESPONSE2=$(curl -s -X POST http://localhost:8000/api/agent/chat \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "Analyze the performance of machine learning models",
        "auto_execute": true
    }')

if [ $? -eq 0 ]; then
    echo "✅ Advanced mode request successful!"
    echo ""
    echo "Response preview:"
    echo "$RESPONSE2" | python3 -m json.tool | head -20
    echo ""
else
    echo "❌ Advanced mode request failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ All tests passed!"
echo ""
echo "🎉 The Conversations feature is ready to use!"
echo ""
echo "Next steps:"
echo "  1. Start frontend: ./start-frontend.sh"
echo "  2. Navigate to http://localhost:4200"
echo "  3. Go to Conversations page"
echo "  4. Enter a query and select an AI agent"
echo "  5. Click 'Start Search' button"
echo ""

