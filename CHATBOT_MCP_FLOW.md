# Chatbot MCP Integration Flow

## Complete Flow Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │  POST   │   Backend    │  CALL   │  MCP Server │  RETURN │   Backend   │
│  (Angular)  │────────>│   Endpoint   │────────>│             │────────>│   Endpoint  │
│             │         │              │         │             │         │             │
└─────────────┘         └──────────────┘         └─────────────┘         └─────────────┘
       │                        │                                              │
       │                        │                                              │
       │                        │                                              │
       │                        ▼                                              │
       │              ┌─────────────────┐                                      │
       │              │  Knowledge Base│                                      │
       │              │  (Save Insights)│                                      │
       │              └─────────────────┘                                      │
       │                                                                       │
       │                        │                                              │
       │                        │                                              │
       └────────────────────────┴──────────────────────────────────────────────┘
                                │
                                │ JSON Response
                                │
                                ▼
                         ┌─────────────┐
                         │   Frontend  │
                         │  (Display)  │
                         └─────────────┘
```

## Step-by-Step Flow

### 1. Frontend Sends Message
**Location:** `src/app/components/chatbot/chatbot.component.ts`

```typescript
// User types message and clicks send
sendMessage() {
  // Frontend sends POST request to backend
  this.http.post(`${this.apiUrl}/chatbot/mcp-message`, {
    message: messageToSend,
    session_id: this.sessionId,
    mcp_server_id: this.selectedMCPServer(),  // Optional
    use_bedrock: this.useBedrock()             // Optional
  })
}
```

### 2. Backend Receives Message
**Location:** `backend/app.py` - `@app.post("/api/chatbot/mcp-message")`

```python
async def send_chatbot_mcp_message(request: ChatbotMCPMessageRequest):
    # 1. Receive message from frontend
    logger.info(f"📨 Received message from frontend: '{request.message}'")
    
    # 2. Create or get session
    session_id = request.session_id or create_new_session()
    
    # 3. Store user message
    user_message = {
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat()
    }
```

### 3. Backend Calls MCP Server
**Location:** `backend/app.py` - `mcp_client.call_mcp_server()`

```python
    # 4. Determine which MCP server to use
    mcp_server_id = request.mcp_server_id or auto_select_server(request.message)
    
    # 5. Prepare MCP call parameters
    mcp_params = {
        "message": request.message,
        "context": session["messages"][-5:]  # Last 5 messages for context
    }
    
    # 6. CALL MCP SERVER - THIS IS THE KEY STEP
    logger.info(f"📞 Calling MCP server '{mcp_server_id}'")
    mcp_response = await mcp_client.call_mcp_server(
        server_id=mcp_server_id,
        method="process_message",
        params=mcp_params
    )
```

### 4. MCP Server Processes Request
**Location:** `backend/app.py` - `MCPClient._process_chat_message()`

```python
async def _process_chat_message(self, server_id: str, params: Dict[str, Any]):
    message = params.get("message", "")
    
    # Process based on server type:
    if server_id == "filesystem":
        # Handle file operations
    elif server_id == "database":
        # Handle database queries
    elif server_id == "web_scraper":
        # Handle web scraping
    
    return {
        "result": "success",
        "data": "Response from MCP server",
        "content": "Processed message content"
    }
```

### 5. Backend Returns Response to Frontend
**Location:** `backend/app.py` - Return statement

```python
    # 7. Extract MCP response
    ai_response_text = mcp_response.get("data", mcp_response.get("content"))
    
    # 8. Optionally enhance with Bedrock (if requested)
    if request.use_bedrock:
        ai_response_text = enhance_with_bedrock(ai_response_text)
    
    # 9. Save to knowledge base
    kb.add_insight(session_id, request.message, ai_response_text, metadata)
    
    # 10. Return response to frontend
    logger.info(f"📤 Sending response back to frontend")
    return {
        "session_id": session_id,
        "user_message": user_message,
        "ai_message": {
            "role": "assistant",
            "content": ai_response_text,
            "mcp_server": mcp_server_id,
            "mcp_response": mcp_response
        },
        "mcp_server": mcp_server_id,
        "mcp_response": mcp_response
    }
```

### 6. Frontend Displays Response
**Location:** `src/app/components/chatbot/chatbot.component.ts`

```typescript
// Frontend receives response
if (response.ai_message) {
  this.messages.update(msgs => [...msgs, response.ai_message]);
}
```

## API Endpoint Details

### Endpoint: `POST /api/chatbot/mcp-message`

**Request Body:**
```json
{
  "message": "List all files in the directory",
  "session_id": "chat_20241120080000_1",  // Optional
  "mcp_server_id": "filesystem",          // Optional (auto-selected if not provided)
  "use_bedrock": false                    // Optional (enhance with Bedrock)
}
```

**Response:**
```json
{
  "session_id": "chat_20241120080000_1",
  "user_message": {
    "role": "user",
    "content": "List all files in the directory",
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

## Available MCP Servers

- **filesystem**: File and directory operations
- **database**: SQL queries and schema inspection  
- **web_scraper**: URL fetching and HTML parsing

## Logging

The endpoint includes comprehensive logging:
- 📨 Message received from frontend
- 🆕 Session creation
- 💬 User message stored
- 🤖 MCP server selection
- 📞 MCP server call
- ✅ MCP server response
- 💾 Knowledge base save
- 📤 Response sent to frontend

## Testing

Use the provided curl examples or test script:

```bash
# Test with curl
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{"message": "List files"}'

# Or use the test script
./test-chatbot-api.sh
```




