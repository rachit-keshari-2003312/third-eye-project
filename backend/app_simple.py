#!/usr/bin/env python3
"""
Third-Eye Backend Server - Simplified Version
Works without MCP SDK installed (uses mock mode)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import smart agent (simplified version that doesn't need MCP SDK)
import re

class SmartAgentSimple:
    """Simplified Smart Agent that works without MCP SDK"""
    
    def __init__(self):
        self.mcp_patterns = {
            'redash-mcp': {
                'keywords': ['query', 'queries', 'dashboard', 'dashboards', 'redash', 'analytics', 'report', 'reports', 'data source', 'sql', 'kpi'],
                'patterns': [r'show.*dashboard', r'list.*queries', r'execute.*query', r'redash.*'],
                'description': 'Redash analytics and data visualization'
            },
            'filesystem': {
                'keywords': ['file', 'files', 'read file', 'write file', 'directory', 'folder', 'list files'],
                'patterns': [r'read.*file', r'write.*file', r'list.*files'],
                'description': 'File system operations'
            },
            'git': {
                'keywords': ['git', 'commit', 'commits', 'repository', 'repo', 'branch', 'git log', 'git status'],
                'patterns': [r'git\s+(status|log|diff|commit)', r'show.*commits'],
                'description': 'Git version control operations'
            },
            'brave-search': {
                'keywords': ['search', 'web search', 'find online', 'look up', 'internet'],
                'patterns': [r'search.*web', r'find.*online', r'look.*up'],
                'description': 'Web search using Brave'
            },
        }
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze a prompt and determine which MCP server to use"""
        prompt_lower = prompt.lower()
        scores = {}
        
        for server_id, config in self.mcp_patterns.items():
            score = 0
            matched_keywords = []
            
            for keyword in config['keywords']:
                if keyword.lower() in prompt_lower:
                    score += 2
                    matched_keywords.append(keyword)
            
            for pattern in config['patterns']:
                if re.search(pattern, prompt_lower):
                    score += 3
            
            if score > 0:
                scores[server_id] = {
                    'score': score,
                    'matched_keywords': matched_keywords,
                    'description': config['description']
                }
        
        if not scores:
            return {
                'server_id': None,
                'confidence': 0,
                'reasoning': 'No matching MCP server found'
            }
        
        best_match = max(scores.items(), key=lambda x: x[1]['score'])
        server_id = best_match[0]
        info = best_match[1]
        
        confidence = min(100, (info['score'] / 20) * 100)
        
        return {
            'server_id': server_id,
            'confidence': round(confidence, 2),
            'matched_keywords': info['matched_keywords'],
            'description': info['description'],
            'reasoning': f"Selected {server_id} based on matching keywords: {', '.join(info['matched_keywords'][:3])}"
        }
    
    async def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process a prompt (mock mode - returns analysis only)"""
        analysis = self.analyze_prompt(prompt)
        
        if not analysis['server_id']:
            return {
                'success': False,
                'error': 'Could not determine which MCP server to use',
                'prompt': prompt,
                'analysis': analysis,
                'mode': 'mock'
            }
        
        # In mock mode, return success with simulated data
        return {
            'success': True,
            'action': 'mock_execution',
            'server_id': analysis['server_id'],
            'tool_name': 'mock_tool',
            'result': {
                'message': 'Mock mode: MCP SDK not installed',
                'note': 'This is a simulation. Real execution requires MCP SDK.',
                'prompt': prompt,
                'selected_server': analysis['server_id']
            },
            'prompt': prompt,
            'analysis': analysis,
            'mode': 'mock'
        }

# Global agent
agent = SmartAgentSimple()

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Third-Eye Backend Server (Simplified Mode)...")
    logger.info("⚠️  Running in MOCK mode - MCP SDK not installed")
    yield
    logger.info("Shutting down...")

# FastAPI app
app = FastAPI(
    title="Third-Eye API (Simplified)",
    description="Agentic AI Platform Backend - Mock Mode",
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
        "message": "Third-Eye Backend API (Simplified Mode)",
        "version": "1.0.0",
        "status": "running",
        "mode": "mock - MCP SDK not installed"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "mock",
        "note": "Running without MCP SDK - install it for full functionality"
    }

@app.post("/api/agent/prompt")
async def process_prompt(request: PromptRequest):
    """Process a user prompt and intelligently route to appropriate MCP server"""
    try:
        result = await agent.process_prompt(request.prompt)
        
        return {
            "success": result.get('success', False),
            "prompt": request.prompt,
            "analysis": result.get('analysis', {}),
            "action": result.get('action'),
            "server_id": result.get('server_id'),
            "tool_name": result.get('tool_name'),
            "result": result.get('result'),
            "error": result.get('error'),
            "mode": "mock",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/analyze")
async def analyze_prompt(request: PromptRequest):
    """Analyze a prompt without executing"""
    try:
        analysis = agent.analyze_prompt(request.prompt)
        
        return {
            "prompt": request.prompt,
            "analysis": analysis,
            "mode": "mock",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/chat")
async def chat_with_agent(request: PromptRequest):
    """Chat-style interaction"""
    try:
        result = await agent.process_prompt(request.prompt)
        analysis = result.get('analysis', {})
        
        response = f"🤖 Smart Agent Analysis:\n"
        response += f"   Selected: {result.get('server_id', 'unknown')}\n"
        response += f"   Confidence: {analysis.get('confidence', 0)}%\n"
        response += f"   Mode: Mock (MCP SDK not installed)\n"
        
        return {
            "prompt": request.prompt,
            "response": response,
            "mode": "mock",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp/servers")
async def get_mcp_servers():
    """List configured MCP servers"""
    return {
        "servers": [
            {
                "id": "redash-mcp",
                "name": "Redash MCP",
                "status": "mock",
                "description": "Redash analytics (mock mode)"
            },
            {
                "id": "filesystem",
                "name": "Filesystem MCP",
                "status": "mock",
                "description": "File operations (mock mode)"
            },
            {
                "id": "git",
                "name": "Git MCP",
                "status": "mock",
                "description": "Git operations (mock mode)"
            },
            {
                "id": "brave-search",
                "name": "Brave Search MCP",
                "status": "mock",
                "description": "Web search (mock mode)"
            }
        ],
        "mode": "mock",
        "note": "Install MCP SDK for real functionality"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Third-Eye Backend Server (Simplified)...")
    logger.info("⚠️  Running in MOCK mode - MCP SDK not installed")
    logger.info("To install MCP SDK: pip3 install mcp")
    
    uvicorn.run(
        "app_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

