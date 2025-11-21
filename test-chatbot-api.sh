#!/bin/bash

# Test script for Chatbot MCP API endpoints
# Usage: ./test-chatbot-api.sh

API_URL="http://localhost:8000/api"

echo "🤖 Testing Chatbot MCP API Endpoints"
echo "===================================="
echo ""

# Test 1: Start a new chat session
echo "📝 Test 1: Starting a new chat session..."
SESSION_RESPONSE=$(curl -s -X POST "${API_URL}/chatbot/start" \
  -H "Content-Type: application/json")

echo "Response: $SESSION_RESPONSE"
echo ""

# Extract session_id (simple extraction, assumes JSON format)
SESSION_ID=$(echo $SESSION_RESPONSE | grep -o '"session_id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$SESSION_ID" ]; then
    echo "⚠️  Could not extract session_id. Using default..."
    SESSION_ID="chat_test_$(date +%Y%m%d%H%M%S)"
fi

echo "✅ Session ID: $SESSION_ID"
echo ""

# Test 2: Send a message via MCP (auto-select server)
echo "📤 Test 2: Sending message via MCP (auto-select)..."
curl -X POST "${API_URL}/chatbot/mcp-message" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"List all files in the directory\",
    \"session_id\": \"$SESSION_ID\"
  }" | jq '.' 2>/dev/null || cat

echo ""
echo ""

# Test 3: Send a message with specific MCP server
echo "📤 Test 3: Sending message with filesystem MCP server..."
curl -X POST "${API_URL}/chatbot/mcp-message" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Show me the directory contents\",
    \"session_id\": \"$SESSION_ID\",
    \"mcp_server_id\": \"filesystem\"
  }" | jq '.' 2>/dev/null || cat

echo ""
echo ""

# Test 4: Send a message with database MCP server
echo "📤 Test 4: Sending message with database MCP server..."
curl -X POST "${API_URL}/chatbot/mcp-message" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Show me all database tables\",
    \"session_id\": \"$SESSION_ID\",
    \"mcp_server_id\": \"database\"
  }" | jq '.' 2>/dev/null || cat

echo ""
echo ""

# Test 5: Get session history
echo "📖 Test 5: Getting session history..."
curl -X GET "${API_URL}/chatbot/session/${SESSION_ID}" \
  -H "Content-Type: application/json" | jq '.' 2>/dev/null || cat

echo ""
echo ""

# Test 6: Get all sessions
echo "📋 Test 6: Getting all chat sessions..."
curl -X GET "${API_URL}/chatbot/sessions" \
  -H "Content-Type: application/json" | jq '.' 2>/dev/null || cat

echo ""
echo ""
echo "✅ All tests completed!"




