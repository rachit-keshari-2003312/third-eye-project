#!/usr/bin/env python3
"""
Third-Eye Backend Server
A Python FastAPI backend that integrates with MCP servers and provides AI agent functionality.
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging
import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import httpx
from contextlib import asynccontextmanager

# Import our MCP client and Smart Agent
from mcp_client import MCPClientManager
from smart_agent import SmartAgent, get_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MCP client manager
mcp_manager: Optional[MCPClientManager] = None

# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mcp_manager
    logger.info("Starting Third-Eye Backend Server...")
    
    # Initialize MCP client manager
    mcp_config_path = os.path.join(os.path.dirname(__file__), "..", "mcp.json")
    mcp_manager = MCPClientManager(config_path=mcp_config_path)
    
    # Load configuration
    await mcp_manager.load_config()
    logger.info("MCP configuration loaded")
    
    # Note: We don't auto-initialize all servers at startup
    # Servers will be initialized on-demand or via API call
    logger.info("MCP manager initialized (servers will connect on-demand)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Third-Eye Backend Server...")
    if mcp_manager:
        await mcp_manager.shutdown_all_servers()
    logger.info("All MCP servers disconnected")

# FastAPI app initialization
app = FastAPI(
    title="Third-Eye API",
    description="Agentic AI Platform Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MCPServer(BaseModel):
    id: str
    name: str
    endpoint: str
    status: str
    capabilities: List[str]
    config: Dict[str, Any] = {}

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
    model: Optional[str] = None

class BedrockRequest(BaseModel):
    model_id: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 1000

class PromptRequest(BaseModel):
    prompt: str
    auto_execute: bool = True

class AgentConfig(BaseModel):
    name: str
    description: str
    type: str
    capabilities: List[str]
    mcp_connections: List[str]

# In-memory storage (in production, use a proper database)
agents: Dict[str, Dict] = {}
conversations: Dict[str, List[ChatMessage]] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# AWS Bedrock Integration
class BedrockClient:
    def __init__(self):
        self.client = None
        self.region = None
        
    def initialize(self, region: str, access_key: str, secret_key: str, session_token: str = None):
        """Initialize Bedrock client with credentials"""
        try:
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token,
                region_name=region
            )
            self.client = session.client('bedrock-runtime')
            self.region = region
            logger.info(f"Bedrock client initialized for region {region}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            return False
    
    async def invoke_model(self, model_id: str, messages: List[ChatMessage], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Invoke a Bedrock model"""
        if not self.client:
            raise HTTPException(status_code=400, detail="Bedrock client not initialized")
        
        try:
            # Convert messages to the format expected by the model
            if "anthropic.claude" in model_id:
                return await self._invoke_claude(model_id, messages, temperature, max_tokens)
            elif "amazon.nova" in model_id:
                return await self._invoke_nova(model_id, messages, temperature, max_tokens)
            else:
                # Generic model invocation
                return await self._invoke_generic(model_id, messages, temperature, max_tokens)
        except ClientError as e:
            logger.error(f"Bedrock invocation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Model invocation failed: {str(e)}")
    
    async def _invoke_claude(self, model_id: str, messages: List[ChatMessage], temperature: float, max_tokens: int) -> str:
        """Invoke Claude model"""
        # Convert messages to Claude format
        claude_messages = []
        for msg in messages:
            claude_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": claude_messages
        }
        
        # For demo purposes, return a mock response
        return "This is a mock response from Claude. In a real implementation, this would call the actual Bedrock API."
    
    async def _invoke_nova(self, model_id: str, messages: List[ChatMessage], temperature: float, max_tokens: int) -> str:
        """Invoke Amazon Nova model"""
        # Mock response for Nova
        return "This is a mock response from Amazon Nova. The model would process your request and return insights."
    
    async def _invoke_generic(self, model_id: str, messages: List[ChatMessage], temperature: float, max_tokens: int) -> str:
        """Invoke generic model"""
        return f"Mock response from {model_id}. This would be the actual model response in production."

bedrock_client = BedrockClient()

# API Routes

@app.get("/")
async def root():
    return {"message": "Third-Eye Backend API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    connected_servers = 0
    if mcp_manager:
        connected_servers = len([s for s in mcp_manager.get_all_servers().values() if s.is_connected])
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mcp_servers": connected_servers,
            "bedrock": bedrock_client.client is not None,
            "mcp_manager": mcp_manager is not None
        }
    }

# MCP Server endpoints
@app.get("/api/mcp/servers")
async def get_mcp_servers():
    """Get all configured MCP servers with their status"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    servers = mcp_manager.get_all_servers_status()
    return {"servers": servers}

@app.post("/api/mcp/servers/{server_id}/connect")
async def connect_mcp_server(server_id: str):
    """Connect to a specific MCP server"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        success = await mcp_manager.initialize_server(server_id)
        if success:
            status = mcp_manager.get_server_status(server_id)
            return {"success": True, "server": status, "message": f"Connected to {server_id}"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to connect to {server_id}")
    except Exception as e:
        logger.error(f"Error connecting to server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mcp/servers/{server_id}/disconnect")
async def disconnect_mcp_server(server_id: str):
    """Disconnect from a specific MCP server"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        await mcp_manager.shutdown_server(server_id)
        return {"success": True, "message": f"Disconnected from {server_id}"}
    except Exception as e:
        logger.error(f"Error disconnecting from server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp/servers/{server_id}/tools")
async def list_server_tools(server_id: str):
    """List all tools available on a specific MCP server"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        tools = await mcp_manager.list_tools(server_id)
        return {"server_id": server_id, "tools": tools}
    except Exception as e:
        logger.error(f"Error listing tools for server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp/tools")
async def list_all_tools():
    """List all tools from all connected MCP servers"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        all_tools = await mcp_manager.list_all_tools()
        return {"tools": all_tools}
    except Exception as e:
        logger.error(f"Error listing all tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mcp/servers/{server_id}/call")
async def call_mcp_tool(server_id: str, request: Dict[str, Any]):
    """Call a tool on a specific MCP server"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    tool_name = request.get("tool_name")
    arguments = request.get("arguments", {})
    
    if not tool_name:
        raise HTTPException(status_code=400, detail="tool_name is required")
    
    try:
        result = await mcp_manager.call_tool(server_id, tool_name, arguments)
        return {"server_id": server_id, "tool_name": tool_name, "result": result}
    except Exception as e:
        logger.error(f"Error calling tool {tool_name} on server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp/servers/{server_id}/resources")
async def list_server_resources(server_id: str):
    """List all resources available on a specific MCP server"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        resources = await mcp_manager.list_resources(server_id)
        return {"server_id": server_id, "resources": resources}
    except Exception as e:
        logger.error(f"Error listing resources for server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mcp/servers/{server_id}/resources/read")
async def read_server_resource(server_id: str, request: Dict[str, Any]):
    """Read a resource from a specific MCP server"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    uri = request.get("uri")
    if not uri:
        raise HTTPException(status_code=400, detail="uri is required")
    
    try:
        result = await mcp_manager.read_resource(server_id, uri)
        return {"server_id": server_id, "uri": uri, "result": result}
    except Exception as e:
        logger.error(f"Error reading resource {uri} from server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Bedrock endpoints
@app.post("/api/bedrock/connect")
async def connect_bedrock(credentials: Dict[str, str]):
    region = credentials.get("region", "us-east-1")
    access_key = credentials.get("accessKeyId")
    secret_key = credentials.get("secretAccessKey")
    session_token = credentials.get("sessionToken")
    
    if not access_key or not secret_key:
        raise HTTPException(status_code=400, detail="Access key and secret key are required")
    
    success = bedrock_client.initialize(region, access_key, secret_key, session_token)
    
    if success:
        return {"status": "connected", "region": region}
    else:
        raise HTTPException(status_code=400, detail="Failed to connect to Bedrock")

@app.post("/api/bedrock/invoke")
async def invoke_bedrock_model(request: BedrockRequest):
    try:
        response = await bedrock_client.invoke_model(
            request.model_id,
            request.messages,
            request.temperature,
            request.max_tokens
        )
        
        return {
            "response": response,
            "model": request.model_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Bedrock invocation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent management endpoints
@app.get("/api/agents")
async def get_agents():
    return {"agents": list(agents.values())}

@app.post("/api/agents")
async def create_agent(agent_config: AgentConfig):
    agent_id = f"agent_{len(agents) + 1}"
    agent = {
        "id": agent_id,
        "name": agent_config.name,
        "description": agent_config.description,
        "type": agent_config.type,
        "capabilities": agent_config.capabilities,
        "mcp_connections": agent_config.mcp_connections,
        "status": "idle",
        "created": datetime.now().isoformat(),
        "conversations": 0
    }
    
    agents[agent_id] = agent
    return {"agent": agent, "message": "Agent created successfully"}

@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str):
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    del agents[agent_id]
    return {"message": f"Agent {agent_id} deleted successfully"}

# Conversation endpoints
@app.get("/api/conversations")
async def get_conversations():
    return {"conversations": conversations}

@app.post("/api/conversations/{conversation_id}/messages")
async def send_message(conversation_id: str, message: ChatMessage):
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    conversations[conversation_id].append(message)
    
    # Process message with AI (mock response)
    ai_response = ChatMessage(
        role="assistant",
        content=f"I understand your message: '{message.content}'. This is a mock response from the AI agent.",
        timestamp=datetime.now()
    )
    
    conversations[conversation_id].append(ai_response)
    
    return {"message": "Message sent", "response": ai_response}

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process the message and send response
            response = {
                "type": "message",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat(),
                "data": f"Echo: {message}"
            }
            
            await manager.send_personal_message(json.dumps(response), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected")

# Smart Agent endpoint - Process prompts intelligently
@app.post("/api/agent/prompt")
async def process_prompt(request: PromptRequest):
    """
    Process a user prompt and intelligently route to appropriate MCP server
    
    This is the main endpoint for frontend integration!
    """
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        # Get or create smart agent
        agent = get_agent(mcp_manager)
        
        # Process the prompt
        result = await agent.process_prompt(request.prompt)
        
        return {
            "success": result.get('success', False),
            "prompt": request.prompt,
            "analysis": result.get('analysis', {}),
            "action": result.get('action'),
            "server_id": result.get('server_id'),
            "tool_name": result.get('tool_name'),
            "result": result.get('result'),
            "available_tools": result.get('available_tools'),
            "error": result.get('error'),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/analyze")
async def analyze_prompt(request: PromptRequest):
    """
    Analyze a prompt without executing (just show which MCP would be used)
    """
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        agent = get_agent(mcp_manager)
        analysis = agent.analyze_prompt(request.prompt)
        
        return {
            "prompt": request.prompt,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/chat")
async def chat_with_agent(request: PromptRequest):
    """
    Chat-style interaction with the smart agent (returns human-readable response)
    """
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        agent = get_agent(mcp_manager)
        response = await agent.chat(request.prompt)
        
        return {
            "prompt": request.prompt,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/api/analytics/usage")
async def get_usage_analytics():
    return {
        "total_requests": 247,
        "total_tokens": 125430,
        "estimated_cost": 18.45,
        "avg_response_time": 1240,
        "active_agents": len([a for a in agents.values() if a.get("status") == "active"]),
        "mcp_calls": 89
    }

# Dashboard Test Endpoints
@app.post("/api/dashboard/test-query")
async def test_dashboard_query():
    """Test endpoint for metric widget generation"""
    return {
        "success": True,
        "prompt": "Show me the total number of CKYC details fetched in the last 30 days",
        "analysis": {"query_type": "count", "time_range": "30 days"},
        "service": "redash",
        "action": "sql_query",
        "result": None,
        "raw_data": {
            "columns": [{"friendly_name": "CKYC Details Fetched", "type": "integer", "name": "ckyc_details_fetched"}],
            "rows": [{"ckyc_details_fetched": 11871}]
        },
        "answer": "In the last 30 days, 11,871 CKYC details have been fetched.",
        "sql": "SELECT COUNT(*) AS ckyc_details_fetched FROM ckyc_details WHERE updated_at >= NOW() - INTERVAL 30 DAY;",
        "explanation": "This query counts rows from the last 30 days.",
        "row_count": 1,
        "data_source_id": 79,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/dashboard/test-table-query")
async def test_dashboard_table_query():
    """Test endpoint for table widget generation"""
    return {
        "success": True,
        "prompt": "Show me the top 5 users by transaction count in the last week",
        "analysis": {"query_type": "aggregation"},
        "service": "redash",
        "action": "sql_query",
        "result": None,
        "raw_data": {
            "columns": [
                {"friendly_name": "User ID", "type": "integer", "name": "user_id"},
                {"friendly_name": "Username", "type": "string", "name": "username"},
                {"friendly_name": "Transaction Count", "type": "integer", "name": "transaction_count"},
                {"friendly_name": "Total Amount", "type": "float", "name": "total_amount"}
            ],
            "rows": [
                {"user_id": 1234, "username": "alice_smith", "transaction_count": 245, "total_amount": 15678.50},
                {"user_id": 5678, "username": "bob_jones", "transaction_count": 198, "total_amount": 12456.75},
                {"user_id": 9012, "username": "carol_white", "transaction_count": 187, "total_amount": 9876.25},
                {"user_id": 3456, "username": "david_brown", "transaction_count": 156, "total_amount": 8234.90},
                {"user_id": 7890, "username": "eve_davis", "transaction_count": 143, "total_amount": 7654.30}
            ]
        },
        "answer": "Top 5 users by transaction count.",
        "sql": "SELECT user_id, username, COUNT(*) as transaction_count, SUM(amount) as total_amount FROM transactions WHERE created_at >= NOW() - INTERVAL 7 DAY GROUP BY user_id, username ORDER BY transaction_count DESC LIMIT 5;",
        "row_count": 5,
        "data_source_id": 79,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/dashboard/test-chart-query")
async def test_dashboard_chart_query():
    """Test endpoint for chart widget generation"""
    return {
        "success": True,
        "prompt": "Show me daily transaction counts for the last 7 days",
        "analysis": {"query_type": "time_series"},
        "service": "redash",
        "action": "sql_query",
        "result": None,
        "raw_data": {
            "columns": [
                {"friendly_name": "Date", "type": "date", "name": "date"},
                {"friendly_name": "Transaction Count", "type": "integer", "name": "transaction_count"},
                {"friendly_name": "Total Amount", "type": "float", "name": "total_amount"}
            ],
            "rows": [
                {"date": "2025-11-14", "transaction_count": 1245, "total_amount": 87650.25},
                {"date": "2025-11-15", "transaction_count": 1398, "total_amount": 92340.50},
                {"date": "2025-11-16", "transaction_count": 1156, "total_amount": 78920.75},
                {"date": "2025-11-17", "transaction_count": 1487, "total_amount": 95670.00},
                {"date": "2025-11-18", "transaction_count": 1623, "total_amount": 102340.25},
                {"date": "2025-11-19", "transaction_count": 1534, "total_amount": 98765.50},
                {"date": "2025-11-20", "transaction_count": 1401, "total_amount": 91234.75}
            ]
        },
        "answer": "Daily transaction breakdown for the last 7 days.",
        "sql": "SELECT DATE(created_at) as date, COUNT(*) as transaction_count, SUM(amount) as total_amount FROM transactions WHERE created_at >= NOW() - INTERVAL 7 DAY GROUP BY DATE(created_at) ORDER BY date;",
        "row_count": 7,
        "data_source_id": 79,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    # Create required directories
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting Third-Eye Backend Server...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
