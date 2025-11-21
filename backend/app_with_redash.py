#!/usr/bin/env python3
"""
Third-Eye Backend - With Direct Redash Integration
Uses direct API calls instead of MCP for Redash
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

# Load environment
load_dotenv()

# Import direct Redash client and Smart Agent
from redash_direct import get_redash_client
from smart_agent_hybrid import get_hybrid_agent
from conversation_memory import get_conversation_memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Redash client and Smart Agent
redash_client = None
smart_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redash_client, smart_agent
    logger.info("🚀 Starting Third-Eye Backend (Prompt-Based with Direct Redash)")
    
    # Initialize Redash client
    redash_client = get_redash_client()
    if redash_client:
        logger.info("✅ Redash client initialized")
    else:
        logger.warning("⚠️  Redash client not available")
    
    # Initialize Smart Agent
    smart_agent = get_hybrid_agent()
    logger.info("✅ Smart Agent initialized")
    
    yield
    logger.info("Shutting down...")

# FastAPI app
app = FastAPI(
    title="Third-Eye API",
    description="Agentic AI Platform with Direct Redash Integration",
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
    session_id: Optional[str] = None  # For conversation memory

class AnalyticsQueryRequest(BaseModel):
    """Frontend compatibility model for /api/analytics/execute"""
    query: str
    output_format: str = "json"
    session_id: Optional[str] = None  # For conversation memory

# Routes
@app.get("/")
async def root():
    return {
        "message": "Third-Eye Backend API",
        "version": "1.0.0",
        "status": "running",
        "mode": "Direct Redash Integration"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "redash_available": redash_client is not None,
        "smart_agent_available": smart_agent is not None
    }

# Smart Agent endpoint (Main prompt endpoint!)
@app.post("/api/agent/prompt")
async def process_prompt_with_agent(request: PromptRequest):
    """
    Main endpoint: Send natural language prompts, get results!
    Examples:
      - "Show me all data sources"
      - "List all queries"
      - "Execute query 123"
    """
    if not smart_agent:
        raise HTTPException(status_code=500, detail="Smart Agent not available")
    
    # Get or create conversation session
    conv_memory = get_conversation_memory()
    session_id = request.session_id
    
    if not session_id:
        session_id = conv_memory.create_session()
    elif session_id not in conv_memory.get_active_sessions():
        logger.warning(f"Invalid session {session_id}, creating new one")
        session_id = conv_memory.create_session()
    
    # Get conversation context
    context = conv_memory.get_context_summary(session_id) if conv_memory.get_history(session_id) else ""
    
    try:
        logger.info(f"Received prompt: {request.prompt} (session: {session_id})")
        result = await smart_agent.process_prompt(request.prompt)
        
        logger.info(f"Result keys: {list(result.keys())}")
        logger.info(f"Has answer: {'answer' in result}")
        logger.info(f"Has llm_intent: {'llm_intent' in result}")
        
        # Store conversation turn
        conv_memory.add_turn(session_id, request.prompt, result)
        
        response = {
            "success": result.get('success', False),
            "prompt": request.prompt,
            "session_id": session_id,  # Return session ID for follow-up queries
            "analysis": result.get('analysis', {}),
            "service": result.get('service'),
            "action": result.get('action'),
            "result": result.get('result'),
            "raw_data": result.get('raw_data'),
            "answer": result.get('answer'),
            "llm_intent": result.get('llm_intent'),
            # SQL-specific fields
            "sql": result.get('sql'),
            "explanation": result.get('explanation'),
            "row_count": result.get('row_count'),
            "data_source_id": result.get('data_source_id'),
            "error": result.get('error'),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add context info if available
        if context:
            response["has_context"] = True
            response["context_turns"] = len(conv_memory.get_history(session_id))
        
        return response
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/analyze")
async def analyze_prompt_only(request: PromptRequest):
    """
    Analyze prompt without executing (preview mode)
    """
    if not smart_agent:
        raise HTTPException(status_code=500, detail="Smart Agent not available")
    
    try:
        analysis = smart_agent.analyze_prompt(request.prompt)
        return {
            "prompt": request.prompt,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analytics/execute")
async def execute_analytics_query(request: AnalyticsQueryRequest):
    """
    Frontend compatibility endpoint - Routes to the AI agent
    This is an alias for /api/agent/prompt to support frontend integration
    
    Example:
        POST /api/analytics/execute
        {
            "query": "Give me last 7 days ckyc count from ckyc_details table",
            "output_format": "json",
            "session_id": "optional-session-id"
        }
    """
    if not smart_agent:
        raise HTTPException(status_code=500, detail="Smart Agent not available")
    
    try:
        logger.info(f"[Analytics API] Received query: {request.query}")
        
        # Get or create conversation session
        conv_memory = get_conversation_memory()
        session_id = request.session_id
        
        if not session_id:
            session_id = conv_memory.create_session()
            logger.info(f"[Analytics API] Created new session: {session_id}")
        elif session_id not in conv_memory.get_active_sessions():
            logger.warning(f"[Analytics API] Invalid session {session_id}, creating new one")
            session_id = conv_memory.create_session()
        else:
            logger.info(f"[Analytics API] Using existing session: {session_id}")
        
        # Get conversation context
        context = conv_memory.get_context_summary(session_id) if conv_memory.get_history(session_id) else ""
        
        # Process with AI agent
        result = await smart_agent.process_prompt(request.query)
        
        # Store conversation turn
        conv_memory.add_turn(session_id, request.query, result)
        
        # Return in frontend-compatible format
        response = {
            "success": result.get('success', False),
            "query_id": f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "query": request.query,
            "prompt": request.query,
            "session_id": session_id,
            "output_format": request.output_format,
            "analysis": result.get('analysis', {}),
            "service": result.get('service'),
            "action": result.get('action'),
            "result": result.get('result'),
            "raw_data": result.get('raw_data'),
            "answer": result.get('answer'),
            "llm_intent": result.get('llm_intent'),
            "sql": result.get('sql'),
            "explanation": result.get('explanation'),
            "row_count": result.get('row_count'),
            "data_source_id": result.get('data_source_id'),
            "error": result.get('error'),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add context info if available
        if context:
            response["has_context"] = True
            response["context_turns"] = len(conv_memory.get_history(session_id))
        
        logger.info(f"[Analytics API] Query processed successfully (session: {session_id})")
        return response
        
    except Exception as e:
        logger.error(f"[Analytics API] Error executing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Redash endpoints
@app.get("/api/redash/data-sources")
async def list_data_sources():
    """List all Redash data sources"""
    if not redash_client:
        raise HTTPException(status_code=500, detail="Redash client not available")
    
    try:
        data_sources = redash_client.list_data_sources()
        return {
            "success": True,
            "data_sources": data_sources,
            "count": len(data_sources)
        }
    except Exception as e:
        logger.error(f"Error listing data sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/redash/data-sources/{data_source_id}")
async def get_data_source(data_source_id: int):
    """Get a specific data source"""
    if not redash_client:
        raise HTTPException(status_code=500, detail="Redash client not available")
    
    try:
        data_source = redash_client.get_data_source(data_source_id)
        return {
            "success": True,
            "data_source": data_source
        }
    except Exception as e:
        logger.error(f"Error getting data source: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/redash/queries")
async def list_queries(page: int = 1, page_size: int = 25):
    """List all Redash queries"""
    if not redash_client:
        raise HTTPException(status_code=500, detail="Redash client not available")
    
    try:
        result = redash_client.list_queries(page=page, page_size=page_size)
        return {
            "success": True,
            "queries": result.get('results', []),
            "count": result.get('count', 0),
            "page": result.get('page', page)
        }
    except Exception as e:
        logger.error(f"Error listing queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/redash/queries/{query_id}")
async def get_query(query_id: int):
    """Get a specific query"""
    if not redash_client:
        raise HTTPException(status_code=500, detail="Redash client not available")
    
    try:
        query = redash_client.get_query(query_id)
        return {
            "success": True,
            "query": query
        }
    except Exception as e:
        logger.error(f"Error getting query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/redash/queries/{query_id}/execute")
async def execute_query(query_id: int):
    """Execute a query"""
    if not redash_client:
        raise HTTPException(status_code=500, detail="Redash client not available")
    
    try:
        result = redash_client.execute_query(query_id)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/redash/dashboards")
async def list_dashboards(page: int = 1, page_size: int = 25):
    """List all dashboards"""
    if not redash_client:
        raise HTTPException(status_code=500, detail="Redash client not available")
    
    try:
        result = redash_client.list_dashboards(page=page, page_size=page_size)
        return {
            "success": True,
            "dashboards": result.get('results', []),
            "count": result.get('count', 0),
            "page": result.get('page', page)
        }
    except Exception as e:
        logger.error(f"Error listing dashboards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Third-Eye Backend with Direct Redash...")
    
    uvicorn.run(
        "app_with_redash:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

