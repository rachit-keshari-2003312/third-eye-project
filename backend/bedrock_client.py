#!/usr/bin/env python3
"""
AWS Bedrock Client for LLM Integration
Uses Claude for intelligent prompt understanding and response generation
"""

import boto3
import json
import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BedrockClient:
    """AWS Bedrock client for Claude LLM"""
    
    def __init__(self, region: str = "us-east-1"):
        """
        Initialize Bedrock client
        
        Args:
            region: AWS region (default: us-east-1)
        """
        self.region = region
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=region
            )
            logger.info(f"✅ Bedrock client initialized in {region}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.bedrock = None
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, 
                         max_tokens: int = 2000) -> str:
        """
        Generate response using Claude via Bedrock
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Max tokens in response
            
        Returns:
            Generated response text
        """
        if not self.bedrock:
            raise Exception("Bedrock client not initialized")
        
        # Use Claude 3 Sonnet
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        
        # Prepare messages
        messages = [{"role": "user", "content": prompt}]
        
        # Prepare request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages
        }
        
        if system_prompt:
            body["system"] = system_prompt
        
        try:
            # Call Bedrock
            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text from content
            content = response_body.get('content', [])
            if content and len(content) > 0:
                return content[0].get('text', '')
            
            return ""
            
        except Exception as e:
            logger.error(f"Error calling Bedrock: {e}")
            raise
    
    def analyze_intent(self, user_prompt: str, available_actions: List[str]) -> Dict[str, Any]:
        """
        Analyze user intent and determine action
        
        Args:
            user_prompt: User's natural language prompt
            available_actions: List of available actions
            
        Returns:
            Dict with action, parameters, and reasoning
        """
        system_prompt = """You are an intelligent data assistant that helps users query their Redash analytics platform.

Your job is to understand the user's intent and determine:
1. What action to take (list_data_sources, list_queries, execute_query, etc.)
2. What parameters are needed
3. How to filter or process the results

Available actions:
- list_data_sources: Get all data sources
- list_queries: Get all queries
- execute_query: Run a specific query (needs query_id)
- get_query: Get query details (needs query_id)

Respond ONLY with a JSON object in this format:
{
  "action": "action_name",
  "parameters": {"param": "value"},
  "filter": "field_to_filter_by if needed",
  "filter_value": "value_to_filter_for",
  "reasoning": "why you chose this action"
}"""

        prompt = f"""User prompt: "{user_prompt}"

Available actions: {', '.join(available_actions)}

What action should be taken and what parameters are needed?"""

        try:
            response = self.generate_response(prompt, system_prompt, max_tokens=500)
            
            # Parse JSON response
            # Extract JSON from response (handle cases where LLM adds explanation)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            
            # Fallback
            return {
                "action": "list_data_sources",
                "parameters": {},
                "reasoning": "Could not parse intent, defaulting to list_data_sources"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return {
                "action": "list_data_sources",
                "parameters": {},
                "reasoning": f"Error: {str(e)}"
            }
    
    def generate_answer(self, user_prompt: str, data: Any, context: str = "") -> str:
        """
        Generate natural language answer based on data
        
        Args:
            user_prompt: Original user prompt
            data: Data fetched from Redash
            context: Additional context
            
        Returns:
            Natural language answer
        """
        system_prompt = """You are a helpful data assistant. 
The user asked a question, and we fetched data from Redash.
Your job is to:
1. Answer their specific question
2. Be concise and direct
3. Highlight the most relevant information
4. Use natural language

If they ask "Can you see X?", answer yes/no and provide key details.
If they ask "Show me Y", present the information clearly.
"""

        # Convert data to string representation
        data_str = json.dumps(data, indent=2)[:3000]  # Limit size
        
        prompt = f"""User asked: "{user_prompt}"

Data retrieved:
{data_str}

{context}

Please provide a clear, direct answer to their question."""

        try:
            return self.generate_response(prompt, system_prompt, max_tokens=1000)
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"I found the data but couldn't generate a response: {str(e)}"


def get_bedrock_client() -> Optional[BedrockClient]:
    """Get configured Bedrock client"""
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    try:
        return BedrockClient(region=region)
    except Exception as e:
        logger.error(f"Failed to create Bedrock client: {e}")
        return None

