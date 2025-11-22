#!/bin/bash
echo "🧪 Testing Knowledge Base API..."

BASE_URL="http://localhost:8000"

echo "1. Testing health endpoint..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

echo "2. Testing root endpoint..."
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""

echo "3. Testing query endpoint..."
curl -s -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What documents do you have in the knowledge base?",
    "model": "openai.gpt-oss-120b-1:0"
  }' | python3 -m json.tool
echo ""

echo "✅ Tests complete!"
