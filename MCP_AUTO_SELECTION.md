# MCP Server Auto-Selection Guide

## Yes! The system automatically redirects to the appropriate MCP server based on your prompt

The endpoint `/api/chatbot/mcp-message` uses **intelligent keyword matching** to automatically select the best MCP server for your message.

## How It Works

### 1. Keyword-Based Scoring System

The system analyzes your message and scores it against different MCP server categories:

- **Filesystem MCP**: File and directory operations
- **Database MCP**: SQL queries and database operations
- **Web Scraper MCP**: URL fetching and web content extraction

### 2. Auto-Selection Process

```
User Message → Keyword Analysis → Score Calculation → Select Highest Score → Route to MCP Server
```

## Examples

### Filesystem MCP (Auto-Selected)

**Keywords that trigger filesystem:**
- file, files, read, write, directory, folder, list files, show files, etc.

**Example prompts:**
```bash
# These will automatically route to filesystem MCP:
"List all files in the directory"
"Read the file example.txt"
"Show me the files in the current folder"
"Create a new file"
"Delete file test.txt"
```

**Curl example:**
```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{"message": "List all files in the directory"}'
# → Automatically routes to "filesystem" MCP server
```

### Database MCP (Auto-Selected)

**Keywords that trigger database:**
- sql, query, database, table, schema, select, insert, update, etc.

**Example prompts:**
```bash
# These will automatically route to database MCP:
"Show me all database tables"
"Run a SQL query"
"List all tables in the database"
"Execute query SELECT * FROM users"
"What's the database schema?"
```

**Curl example:**
```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all database tables"}'
# → Automatically routes to "database" MCP server
```

### Web Scraper MCP (Auto-Selected)

**Keywords that trigger web scraper:**
- url, web, scrape, html, fetch, website, webpage, extract data, etc.

**Example prompts:**
```bash
# These will automatically route to web_scraper MCP:
"Fetch content from https://example.com"
"Scrape the webpage"
"Extract data from the URL"
"Get HTML content from a website"
"Parse the web page"
```

**Curl example:**
```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Fetch content from https://example.com"}'
# → Automatically routes to "web_scraper" MCP server
```

## Manual Override

You can also **manually specify** which MCP server to use:

```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Any message here",
    "mcp_server_id": "filesystem"
  }'
```

## Default Behavior

If no keywords match any category, the system defaults to **filesystem MCP**:

```bash
curl -X POST http://localhost:8000/api/chatbot/mcp-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
# → Defaults to "filesystem" MCP server
```

## Scoring System Details

The system uses a **scoring mechanism**:

1. **Counts keyword matches** for each MCP server category
2. **Selects the server** with the highest score
3. **Logs the selection** for debugging

**Example:**
```
Message: "Read the file and query the database"
Scores:
  - filesystem: 1 (matched "file")
  - database: 1 (matched "query", "database")
  - web_scraper: 0

Result: Routes to "database" (highest score: 1, but database has 2 matches)
```

## Logging

The system logs the auto-selection process:

```
🤖 Auto-selected MCP server: filesystem (score: 2)
📊 Server scores: {'filesystem': 2, 'database': 0, 'web_scraper': 0}
```

## Frontend Integration

The frontend chatbot component automatically uses this feature:

```typescript
// Frontend sends message without specifying MCP server
this.http.post('/api/chatbot/mcp-message', {
  message: "List all files",  // No mcp_server_id specified
  session_id: this.sessionId
})

// Backend automatically selects "filesystem" based on keywords
```

## Summary

✅ **Yes, it automatically redirects!**

- No need to specify `mcp_server_id` in most cases
- System analyzes your message and selects the best MCP server
- Uses intelligent keyword matching with scoring
- Falls back to filesystem if no matches found
- You can still manually override if needed

Just send your message and let the system figure out the best MCP server to use! 🚀




