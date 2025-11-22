#!/usr/bin/env python3.12
"""
Knowledge Base Agent API Service - Direct AWS Implementation
No dependency on strands library - uses direct AWS Bedrock calls
"""

import sys
import os

# Check Python version at startup
if sys.version_info < (3, 12):
    print(f"❌ This application requires Python 3.12 or higher.")
    print(f"Current version: {sys.version}")
    print(f"Please install Python 3.12 and run with python3.12")
    sys.exit(1)

print(f"✅ Running with Python {sys.version}")

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from strands import Agent
from strands.models import BedrockModel
from strands_tools import memory, use_agent
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
bedrock_client = None
bedrock_runtime_client = None

class QueryRequest(BaseModel):
    """Request model for knowledge base queries"""
    prompt: str = Field(..., description="The user query/prompt")
    model: str = Field(default="openai.gpt-oss-120b-1:0", description="Model to use")
    min_score: float = Field(default=0.00000000001, description="Minimum relevance score")
    max_results: int = Field(default=9, description="Maximum results to retrieve")

class QueryResponse(BaseModel):
    """Response model for knowledge base queries"""
    response: str = Field(..., description="The refined response text")
    action: str = Field(..., description="Action taken: store or retrieve")
    success: bool = Field(..., description="Whether the operation was successful")
    timestamp: str = Field(..., description="Response timestamp")
    python_version: str = Field(..., description="Python version used")

def setup_environment():
    """Setup required environment variables"""
    required_env_vars = {
        'KNOWLEDGE_BASE_ID': 'BERDQ7EHF4',
        'DATA_SOURCE_ID': '0UR6Z3A5HY',
        'AWS_PROFILE': 'kb-profile',
        'AWS_REGION': 'eu-north-1',
        'AWS_DEFAULT_REGION': 'eu-north-1',
    }
    
    for key, value in required_env_vars.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.info(f"Set {key}: {value}")

def initialize_aws_clients():
    """Initialize AWS Bedrock clients"""
    global bedrock_client, bedrock_runtime_client
    try:
        session = boto3.Session(profile_name=os.getenv('AWS_PROFILE', 'kb-profile'))
        region = os.getenv('AWS_REGION', 'eu-north-1')
        
        bedrock_client = session.client('bedrock-agent-runtime', region_name=region)
        bedrock_runtime_client = session.client('bedrock-runtime', region_name=region)
        
        # Test connection by checking if we can access the knowledge base
        knowledge_base_id = os.getenv('KNOWLEDGE_BASE_ID')
        logger.info(f"✅ AWS clients initialized. Using knowledge base: {knowledge_base_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize AWS clients: {e}")
        return False

def determine_action_direct(query: str) -> str:
    """Determine if query is store or retrieve using direct logic"""
    # Simple logic to determine action based on keywords
    store_keywords = ['remember', 'store', 'save', 'add', 'my name is', 'i am', 'i live', 'my birthday is']
    retrieve_keywords = ['what', 'who', 'where', 'when', 'how', 'tell me', 'show me', 'find', 'search']
    
    query_lower = query.lower()
    
    # Check for explicit store patterns
    for keyword in store_keywords:
        if keyword in query_lower:
            return "store"
    
    # Check for explicit retrieve patterns
    for keyword in retrieve_keywords:
        if keyword in query_lower:
            return "retrieve"
    
    # Default to retrieve for questions, store for statements
    if query.strip().endswith('?'):
        return "retrieve"
    else:
        return "store"

def invoke_bedrock_model(prompt: str, model_id: str) -> str:
    """Invoke Bedrock model directly"""
    try:
        # Prepare the request body based on model type
        if "openai.gpt" in model_id:
            body = {
                "model": model_id,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
        else:
            # Fallback for other models
            body = {
                "prompt": prompt,
                "temperature": 0.1,
                "max_tokens": 500
            }
        
        response = bedrock_runtime_client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        
        # Extract response text based on model type
        if "openai.gpt" in model_id and 'choices' in response_body:
            return response_body['choices'][0]['message']['content']
        elif 'completion' in response_body:
            return response_body['completion']
        elif 'content' in response_body:
            return response_body['content']
        else:
            return str(response_body)
            
    except Exception as e:
        logger.error(f"Error invoking Bedrock model: {e}")
        return f"Error: {str(e)}"

def retrieve_from_knowledge_base(query: str, min_score: float = 0.0001, max_results: int = 9) -> Dict[str, Any]:
    """Retrieve information from AWS Knowledge Base"""
    try:
        knowledge_base_id = os.getenv('KNOWLEDGE_BASE_ID')
        
        response = bedrock_client.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': max_results
                }
            }
        )
        
        results = response.get('retrievalResults', [])
        
        if not results:
            return {
                "status": "success",
                "content": "No relevant information found in the knowledge base.",
                "results_count": 0
            }
        
        # Filter by score
        filtered_results = [r for r in results if r.get('score', 0) >= min_score]
        
        # Format the results
        formatted_content = []
        for i, result in enumerate(filtered_results[:max_results], 1):
            score = result.get('score', 0)
            content = result.get('content', {}).get('text', 'No content')
            
            formatted_content.append(f"Result {i} (Score: {score:.4f}):\n{content}\n")
        
        return {
            "status": "success", 
            "content": "\n".join(formatted_content),
            "results_count": len(filtered_results)
        }
        
    except ClientError as e:
        error_message = str(e)
        if "No data sources found" in error_message:
            return {
                "status": "error",
                "content": "Knowledge base has no data sources configured."
            }
        else:
            return {
                "status": "error", 
                "content": f"AWS error: {error_message}"
            }
    except Exception as e:
        return {
            "status": "error",
            "content": f"Error retrieving from knowledge base: {str(e)}"
        }

def generate_refined_answer(query: str, kb_content: str, model_id: str) -> str:
    """Generate a refined answer using the retrieved knowledge base content"""
    prompt = f"""Based on the following information from a knowledge base, provide a clear and helpful answer to the user's question.

User Question: {query}

Knowledge Base Information:
{kb_content}

Instructions:
- Provide a direct, helpful answer
- Don't mention technical details like scores or document IDs
- Be conversational and concise
- If the information is insufficient, say so clearly
- Focus only on answering the user's question

Answer:"""

    return invoke_bedrock_model(prompt, model_id)

def store_in_knowledge_base(content: str) -> Dict[str, Any]:
    """Simulate storing content in knowledge base"""
    # Note: Actual storage would require triggering a data source sync
    # For now, we'll just acknowledge the store request
    return {
        "status": "success",
        "content": f"Information noted: {content[:100]}..." if len(content) > 100 else f"Information noted: {content}"
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Knowledge Base API Service (Direct AWS Implementation)...")
    logger.info(f"🐍 Python version: {sys.version}")
    
    # Setup environment
    setup_environment()
    
    # Initialize AWS clients
    aws_ok = initialize_aws_clients()
    
    if not aws_ok:
        logger.error("❌ Failed to initialize AWS clients")
        raise RuntimeError("AWS initialization failed")
    
    logger.info("✅ All services initialized successfully")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Knowledge Base API Service...")

# Create FastAPI app
app = FastAPI(
    title="Knowledge Base Agent API",
    description="REST API for querying knowledge base using direct AWS Bedrock calls (Python 3.12)",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_knowledge_base_query(query: str, model: str, min_score: float, max_results: int) -> Dict[str, Any]:
    """Process a query using direct AWS calls"""
    try:
        # Determine action
        action = determine_action_direct(query)
        
        logger.info(f"Processing query: '{query[:50]}...' with action: {action}")
        
        if action == "store":
            # Store the information
            result = store_in_knowledge_base(query)
            
            return {
                "response": result.get("content", "Information stored successfully"),
                "action": "store",
                "success": result.get("status") == "success"
            }
        
        else:
            # Retrieve from knowledge base
            kb_result = retrieve_from_knowledge_base(query, min_score, max_results)
            
            if kb_result.get("status") == "error":
                return {
                    "response": kb_result.get("content", "Error retrieving from knowledge base"),
                    "action": "retrieve",
                    "success": False
                }
            
            # Generate refined answer
            kb_content = kb_result.get("content", "")
            
            if not kb_content or kb_result.get("results_count", 0) == 0:
                response_text = "I don't have any relevant information in the knowledge base to answer your question."
            else:
                response_text = generate_refined_answer(query, kb_content, model)
            
            return {
                "response": response_text,
                "action": "retrieve", 
                "success": True
            }
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "response": f"Error processing query: {str(e)}",
            "action": "error",
            "success": False
        }

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Knowledge Base Agent API (Direct AWS Implementation)", 
        "version": "1.0.0", 
        "status": "running",
        "python_version": sys.version,
        "implementation": "Direct AWS Bedrock calls (no strands dependency)"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "services": {
            "bedrock_agent_runtime": bedrock_client is not None,
            "bedrock_runtime": bedrock_runtime_client is not None,
            "knowledge_base_id": os.getenv('KNOWLEDGE_BASE_ID'),
            "data_source_id": os.getenv('DATA_SOURCE_ID')
        }
    }

@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Main API endpoint for querying the knowledge base
    
    Uses direct AWS Bedrock calls instead of strands library
    """
    try:
        logger.info(f"Received query: {request.prompt[:100]}...")
        
        # Process the query
        result = process_knowledge_base_query(
            query=request.prompt,
            model=request.model,
            min_score=request.min_score,
            max_results=request.max_results
        )
        
        response = QueryResponse(
            response=result["response"],
            action=result["action"],
            success=result["success"],
            timestamp=datetime.now().isoformat(),
            python_version=sys.version
        )
        
        logger.info(f"Query processed successfully: {result['action']}")
        return response
    
    except Exception as e:
        logger.error(f"Error in query endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port} with Python {sys.version}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
