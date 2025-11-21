#!/usr/bin/env python3
"""
Third-Eye Minimal Backend Server
A simplified FastAPI backend for the conversation feature
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Third-Eye API",
    description="Agentic AI Platform Backend - Minimal Version",
    version="1.0.0"
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
class ConversationRequest(BaseModel):
    agent_type: str
    query_text: str
    include_context: bool = True

class AnalyticsQueryRequest(BaseModel):
    query: str
    output_format: str = "json"

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
    model: Optional[str] = None

# In-memory storage
conversations: Dict[str, List[ChatMessage]] = {}
query_history: List[Dict[str, Any]] = []

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Third-Eye Backend",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/conversations/start")
async def start_conversation(request: ConversationRequest):
    """
    Start a new conversation with the selected agent type.
    This endpoint is called when the user clicks 'Start Search' button.
    """
    try:
        # Generate conversation ID
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.agent_type}"
        
        # Initialize conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Create user message
        user_message = ChatMessage(
            role="user",
            content=request.query_text,
            timestamp=datetime.now()
        )
        conversations[conversation_id].append(user_message)
        
        logger.info(f"Processing query with agent: {request.agent_type}")
        logger.info(f"Query: {request.query_text}")
        
        # Generate mock response based on agent type
        response_content = generate_agent_response(request.agent_type, request.query_text)
        
        # Create AI response
        ai_response = ChatMessage(
            role="assistant",
            content=response_content,
            timestamp=datetime.now(),
            model=request.agent_type
        )
        conversations[conversation_id].append(ai_response)
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "agent_type": request.agent_type,
            "query": request.query_text,
            "response": ai_response.model_dump(),
            "result": {
                "status": "processed",
                "agent": request.agent_type,
                "message": response_content,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_agent_response(agent_type: str, query: str) -> str:
    """Generate a mock response based on agent type"""
    
    responses = {
        "auto": f"🤖 Auto Agent: I've analyzed your query '{query}'. This is an intelligent response that would normally come from the AI system. The query has been processed successfully.",
        
        "redash": f"📊 Redash Agent: I can help you with data analytics for '{query}'. I would typically connect to your Redash instance to execute SQL queries and retrieve data visualizations. Your data request is being processed.",
        
        "slack": f"💬 Slack Agent: I can interact with Slack for '{query}'. Normally, I would search through Slack messages, post notifications, or retrieve team communications. Your Slack operation is ready.",
        
        "git": f"🔧 Git Agent: I can help with Git operations for '{query}'. I would typically analyze repositories, check commit history, or manage branches. Your Git request has been noted.",
        
        "general": f"✨ General Agent: I understand your query '{query}'. I'm a versatile AI agent that can help with various tasks including information retrieval, analysis, and recommendations. How can I assist you further?"
    }
    
    return responses.get(agent_type, f"🤖 {agent_type.title()} Agent: I've received your query '{query}' and I'm processing it with specialized capabilities. Your request has been acknowledged and is being handled.")

@app.get("/api/conversations")
async def get_conversations():
    return {"conversations": conversations}

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }

@app.post("/api/analytics/execute")
async def execute_analytics_query(request: AnalyticsQueryRequest):
    """
    Execute an analytics query.
    This endpoint is called when the user clicks 'Execute Query' button in Analytics page.
    """
    try:
        query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Executing analytics query: {request.query}")
        
        # Generate mock analytics response based on query content
        result = generate_analytics_response(request.query, request.output_format)
        
        # Store in history
        query_record = {
            "query_id": query_id,
            "query": request.query,
            "output_format": request.output_format,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        query_history.append(query_record)
        
        return {
            "success": True,
            "query_id": query_id,
            "query": request.query,
            "output_format": request.output_format,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing analytics query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_analytics_response(query: str, output_format: str) -> Dict[str, Any]:
    """Generate a mock analytics response based on query content"""
    
    query_lower = query.lower()
    
    # Funnel data response
    if any(keyword in query_lower for keyword in ['funnel', 'status', 'stage', 'application']):
        return {
            "success": True,
            "prompt": query,
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "analysis": {
                "type": "funnel_analysis",
                "total_records": 4,
                "date_range": "last_7_days"
            },
            "service": "redash",
            "action": "sql_query",
            "result": None,
            "raw_data": {
                "columns": [
                    {"friendly_name": "Status", "type": "string", "name": "current_status"},
                    {"friendly_name": "Count", "type": "integer", "name": "count"}
                ],
                "rows": [
                    {"count": 21123, "current_status": "CREATED"},
                    {"count": 7993, "current_status": "APPLICATION_APPROVED"},
                    {"count": 3456, "current_status": "UTR_RECEIVED"},
                    {"count": 2134, "current_status": "COMPLETED"}
                ]
            },
            "answer": "Here's the funnel data showing the progression of applications through different stages. There are 21,123 applications in the CREATED stage, 7,993 have been approved, 3,456 have received UTR, and 2,134 are completed. This represents a conversion rate of approximately 10% from creation to completion.",
            "sql": "SELECT ast.current_status, COUNT(*) AS count FROM a_application_stage_tracker ast WHERE ast.created_at >= NOW() - INTERVAL 7 DAY GROUP BY ast.current_status;",
            "explanation": "This query retrieves the funnel data by counting applications in each status stage for the last 7 days.",
            "row_count": 4,
            "data_source_id": 79,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
    
    # Revenue/Sales data response
    elif any(keyword in query_lower for keyword in ['revenue', 'sales', 'product', 'category']):
        return {
            "success": True,
            "prompt": query,
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "analysis": {
                "type": "revenue_analysis",
                "total_revenue": 141680,
                "categories": 5
            },
            "service": "redash",
            "action": "sql_query",
            "raw_data": {
                "columns": [
                    {"friendly_name": "Category", "type": "string", "name": "category"},
                    {"friendly_name": "Revenue", "type": "integer", "name": "revenue"}
                ],
                "rows": [
                    {"category": "Electronics", "revenue": 45230},
                    {"category": "Clothing", "revenue": 32150},
                    {"category": "Home & Garden", "revenue": 28900},
                    {"category": "Sports", "revenue": 19800},
                    {"category": "Books", "revenue": 15600}
                ]
            },
            "answer": "Revenue breakdown by product category shows Electronics leading with $45,230, followed by Clothing at $32,150. Total revenue across all categories is $141,680.",
            "sql": "SELECT category, SUM(revenue) as revenue FROM products GROUP BY category ORDER BY revenue DESC;",
            "explanation": "This query aggregates revenue by product category and orders them by highest revenue.",
            "row_count": 5,
            "timestamp": datetime.now().isoformat()
        }
    
    # User engagement data response
    elif any(keyword in query_lower for keyword in ['user', 'engagement', 'active', 'daily']):
        return {
            "success": True,
            "prompt": query,
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "analysis": {
                "type": "user_engagement",
                "total_users": 60640,
                "peak_day": "Friday"
            },
            "service": "redash",
            "action": "sql_query",
            "raw_data": {
                "columns": [
                    {"friendly_name": "Day", "type": "string", "name": "day"},
                    {"friendly_name": "Active Users", "type": "integer", "name": "users"}
                ],
                "rows": [
                    {"day": "Monday", "users": 8450},
                    {"day": "Tuesday", "users": 9120},
                    {"day": "Wednesday", "users": 8890},
                    {"day": "Thursday", "users": 9560},
                    {"day": "Friday", "users": 10230},
                    {"day": "Saturday", "users": 7650},
                    {"day": "Sunday", "users": 6890}
                ]
            },
            "answer": "Weekly user engagement shows peak activity on Friday with 10,230 active users, and lowest on Sunday with 6,890 users. Average daily active users is 8,670.",
            "sql": "SELECT DATE_FORMAT(created_at, '%W') as day, COUNT(DISTINCT user_id) as users FROM user_activity WHERE created_at >= NOW() - INTERVAL 7 DAY GROUP BY day;",
            "explanation": "This query counts active users by day of the week for the last 7 days.",
            "row_count": 7,
            "timestamp": datetime.now().isoformat()
        }
    
    # Channel performance data response
    elif any(keyword in query_lower for keyword in ['channel', 'source', 'performance']):
        return {
            "success": True,
            "prompt": query,
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "analysis": {
                "type": "channel_performance",
                "total_applications": 51086,
                "top_channel": "EDI_PP_01"
            },
            "service": "redash",
            "action": "sql_query",
            "raw_data": {
                "columns": [
                    {"friendly_name": "Channel", "type": "string", "name": "channel_name"},
                    {"friendly_name": "Applications", "type": "integer", "name": "total_applications"}
                ],
                "rows": [
                    {"channel_name": "EDI_PP_01", "total_applications": 15234},
                    {"channel_name": "WEB_DIRECT", "total_applications": 12890},
                    {"channel_name": "MOBILE_APP", "total_applications": 9876},
                    {"channel_name": "PARTNER_API", "total_applications": 7654},
                    {"channel_name": "BRANCH", "total_applications": 5432}
                ]
            },
            "answer": "Channel performance analysis shows EDI_PP_01 leading with 15,234 applications, followed by WEB_DIRECT with 12,890. Total applications across all channels: 51,086.",
            "sql": "SELECT channel_name, COUNT(*) as total_applications FROM applications GROUP BY channel_name ORDER BY total_applications DESC;",
            "explanation": "This query counts total applications by channel source.",
            "row_count": 5,
            "timestamp": datetime.now().isoformat()
        }
    
    # Default generic response
    else:
        return {
            "success": True,
            "prompt": query,
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "analysis": {
                "type": "general_query",
                "status": "processed"
            },
            "service": "analytics",
            "action": "data_query",
            "raw_data": {
                "columns": [
                    {"friendly_name": "Metric", "type": "string", "name": "metric"},
                    {"friendly_name": "Value", "type": "integer", "name": "value"}
                ],
                "rows": [
                    {"metric": "Total Records", "value": 10000},
                    {"metric": "Processed", "value": 8500},
                    {"metric": "Pending", "value": 1500}
                ]
            },
            "answer": f"I've processed your analytics query: '{query}'. The system has analyzed the data and generated results. Total records: 10,000 with 8,500 processed and 1,500 pending.",
            "sql": "SELECT metric, value FROM analytics_summary;",
            "explanation": "This query retrieves summary analytics data.",
            "row_count": 3,
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/analytics/history")
async def get_query_history():
    """Get analytics query history"""
    return {
        "success": True,
        "history": query_history,
        "total": len(query_history)
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Third-Eye Minimal Backend Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

