#!/usr/bin/env python3
"""
Third-Eye Backend Server - REAL MCP Implementation
No Python MCP SDK needed - calls MCP servers directly via subprocess!
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
logger = logging.getLogger(__name__)
logger.info(f"Loaded REDASH_URL: {os.getenv('REDASH_URL')}")

# Import REAL MCP client and Smart Agent
from mcp_client_real import MCPClientManager
from smart_agent import SmartAgent, get_agent

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global MCP manager
mcp_manager: Optional[MCPClientManager] = None

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_manager
    logger.info("🚀 Starting Third-Eye Backend Server (REAL MODE)")
    
    # Initialize MCP manager
    mcp_manager = MCPClientManager(config_path="../mcp.json")
    await mcp_manager.load_config()
    logger.info("✅ MCP configuration loaded")
    logger.info("✅ MCP servers ready (will connect on-demand)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if mcp_manager:
        await mcp_manager.shutdown_all_servers()

# FastAPI app
app = FastAPI(
    title="Third-Eye API",
    description="Agentic AI Platform Backend - REAL MODE",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class PromptRequest(BaseModel):
    prompt: str
    auto_execute: bool = True

# Routes
@app.get("/")
async def root():
    return {
        "message": "Third-Eye Backend API",
        "version": "1.0.0",
        "status": "running",
        "mode": "REAL - Full MCP functionality"
    }

@app.get("/health")
async def health_check():
    connected_servers = 0
    if mcp_manager:
        connected_servers = len([s for s in mcp_manager.servers.values() if s.is_connected])
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mcp_servers_connected": connected_servers,
        "mode": "real"
    }

@app.post("/api/agent/prompt")
async def process_prompt(request: PromptRequest):
    """Main endpoint - Process prompts and return results"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        agent = get_agent(mcp_manager)
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
            "mode": "real",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/analyze")
async def analyze_prompt(request: PromptRequest):
    """Analyze prompt without executing"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        agent = get_agent(mcp_manager)
        analysis = agent.analyze_prompt(request.prompt)
        
        return {
            "prompt": request.prompt,
            "analysis": analysis,
            "mode": "real",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/chat")
async def chat_with_agent(request: PromptRequest):
    """Chat-style responses"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        agent = get_agent(mcp_manager)
        response = await agent.chat(request.prompt)
        
        return {
            "prompt": request.prompt,
            "response": response,
            "mode": "real",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp/servers")
async def get_mcp_servers():
    """Get all MCP servers status"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    servers = mcp_manager.get_all_servers_status()
    return {"servers": servers, "mode": "real"}

@app.post("/api/mcp/servers/{server_id}/connect")
async def connect_mcp_server(server_id: str):
    """Connect to an MCP server"""
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
        logger.error(f"Error connecting to {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mcp/servers/{server_id}/disconnect")
async def disconnect_mcp_server(server_id: str):
    """Disconnect from an MCP server"""
    if not mcp_manager:
        raise HTTPException(status_code=500, detail="MCP manager not initialized")
    
    try:
        await mcp_manager.shutdown_server(server_id)
        return {"success": True, "message": f"Disconnected from {server_id}"}
    except Exception as e:
        logger.error(f"Error disconnecting from {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Third-Eye Backend Server (REAL MODE)...")
    logger.info("✅ Full MCP functionality via subprocess")
    
    uvicorn.run(
        "app_real:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

