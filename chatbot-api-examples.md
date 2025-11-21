# Chatbot API Endpoint Examples

## MCP-Based Chat Endpoint

### 1. Start a Chat Session

```bash
curl -X POST http://localhost:8000/api/chatbot/start \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "session_id": "chat_20241120080000_1",
  "messages": [],
  "created_at": "2024-11-20T08:00:00"
}
```

### 2. Send a Message via MCP Server (Auto-select MCP server)

```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List all files in the directory",
    "session_id": "chat_20241120080000_1"
  }'
```

### 3. Send a Message with Specific MCP Server

```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me the database tables",
    "session_id": "chat_20241120080000_1",
    "mcp_server_id": "database"
  }'
```

### 4. Send a Message with Bedrock Enhancement

```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Read the file example.txt",
    "session_id": "chat_20241120080000_1",
    "mcp_server_id": "filesystem",
    "use_bedrock": true
  }'
```

### 5. Complete Example - New Chat Session

```bash
# Step 1: Start a new session
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/chatbot/start \
  -H "Content-Type: application/json")

# Extract session_id (requires jq or manual parsing)
SESSION_ID=$(echo $SESSION_RESPONSE | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)

# Step 2: Send a message
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"What files are in the current directory?\",
    \"session_id\": \"$SESSION_ID\"
  }"
```

### 6. Example with Different MCP Servers

**Filesystem Operations:**
```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List directory contents",
    "mcp_server_id": "filesystem"
  }'
```

**Database Operations:**
```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all tables in the database",
    "mcp_server_id": "database"
  }'
```

**Web Scraper Operations:**
```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Fetch content from a URL",
    "mcp_server_id": "web_scraper"
  }'
```

### 7. Get Chat Session History

```bash
curl -X GET http://localhost:8000/api/chatbot/session/chat_20241120080000_1
```

### 8. Get All Chat Sessions

```bash
curl -X GET http://localhost:8000/api/chatbot/sessions
```

## Available MCP Servers

- `filesystem` - File and directory operations
- `database` - SQL queries and schema inspection
- `web_scraper` - URL fetching and HTML parsing

## Request Body Parameters

- `message` (required): The chat message to send
- `session_id` (optional): Existing session ID, or new session will be created
- `mcp_server_id` (optional): Specific MCP server to use. If not provided, auto-selected based on message content
- `use_bedrock` (optional, default: false): Whether to enhance the MCP response with Bedrock AI

## Response Format

```json
{
  "session_id": "chat_20241120080000_1",
  "user_message": {
    "role": "user",
    "content": "List all files",
    "timestamp": "2024-11-20T08:00:00"
  },
  "ai_message": {
    "role": "assistant",
    "content": "Directory listing: file1.txt, file2.py, data.json",
    "timestamp": "2024-11-20T08:00:01",
    "model": "mcp_filesystem",
    "mcp_server": "filesystem",
    "mcp_response": {
      "result": "success",
      "data": "...",
      "content": "..."
    }
  },
  "mcp_server": "filesystem",
  "mcp_response": {...},
  "bedrock_enhanced": false
}
```




