#!/usr/bin/env python3
"""
Smart Agent - Hybrid Version with AWS Bedrock LLM + Autonomous SQL
Uses direct Redash API + AWS Bedrock for intelligent responses
Includes autonomous Text-to-SQL capabilities
"""

import re
import logging
from typing import Dict, Any, List, Optional
from redash_direct import get_redash_client
from bedrock_client import get_bedrock_client
from redash_sql_executor import RedashSQLExecutor
from text_to_sql_agent import TextToSQLAgent

logger = logging.getLogger(__name__)


class SmartAgentHybrid:
    """
    Intelligent agent that analyzes prompts and routes to appropriate services
    - Redash: Uses direct API
    - Other tools: Uses MCP
    """
    
    def __init__(self):
        self.redash_client = get_redash_client()
        self.bedrock_client = get_bedrock_client()
        
        # Initialize SQL executor and Text-to-SQL agent
        import os
        redash_url = os.getenv('REDASH_URL')
        redash_api_key = os.getenv('REDASH_API_KEY')
        
        self.sql_executor = None
        self.text_to_sql_agent = None
        
        if redash_url and redash_api_key and self.bedrock_client:
            self.sql_executor = RedashSQLExecutor(redash_url, redash_api_key)
            self.text_to_sql_agent = TextToSQLAgent(self.bedrock_client, self.sql_executor)
            logger.info("✅ Text-to-SQL agent initialized")
        else:
            logger.warning("⚠️ Text-to-SQL agent not available (missing credentials or Bedrock)")
        
        logger.info(f"SmartAgentHybrid initialized:")
        logger.info(f"  - Redash client: {'✅ Available' if self.redash_client else '❌ None'}")
        logger.info(f"  - Bedrock client: {'✅ Available' if self.bedrock_client else '❌ None'}")
        logger.info(f"  - Text-to-SQL: {'✅ Available' if self.text_to_sql_agent else '❌ None'}")
        
        # Available actions for LLM
        self.available_actions = [
            'list_data_sources',
            'list_queries', 
            'execute_query',
            'get_query',
            'list_dashboards',
            'sql_query'  # New action for data questions
        ]
        
        # Define keywords and patterns for routing
        self.routing_patterns = {
            'redash': {
                'keywords': [
                    'query', 'queries', 'dashboard', 'dashboards', 'visualization',
                    'redash', 'analytics', 'report', 'reports', 'data source',
                    'data sources', 'datasource', 'datasources', 'database',
                    'sql', 'chart', 'graph', 'metrics', 'kpi'
                ],
                'patterns': [
                    r'show.*dashboard',
                    r'list.*queries',
                    r'execute.*query',
                    r'run.*query',
                    r'data.*source',
                    r'redash.*',
                ],
                'description': 'Redash analytics and data visualization'
            },
            'filesystem': {
                'keywords': ['file', 'files', 'directory', 'folder'],
                'patterns': [r'read.*file', r'list.*files'],
                'description': 'File system operations'
            },
            'git': {
                'keywords': ['git', 'commit', 'repository', 'branch'],
                'patterns': [r'git\s+(status|log|diff)'],
                'description': 'Git version control'
            }
        }
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt and determine routing"""
        prompt_lower = prompt.lower()
        scores = {}
        
        for service, config in self.routing_patterns.items():
            score = 0
            matched_keywords = []
            
            for keyword in config['keywords']:
                if keyword in prompt_lower:
                    score += 2
                    matched_keywords.append(keyword)
            
            for pattern in config['patterns']:
                if re.search(pattern, prompt_lower):
                    score += 3
            
            if score > 0:
                scores[service] = {
                    'score': score,
                    'matched_keywords': matched_keywords,
                    'description': config['description']
                }
        
        if not scores:
            return {
                'service': None,
                'confidence': 0,
                'reasoning': 'No matching service found'
            }
        
        best_match = max(scores.items(), key=lambda x: x[1]['score'])
        service = best_match[0]
        info = best_match[1]
        
        confidence = min(100, (info['score'] / 20) * 100)
        
        # Determine specific action
        action = self._determine_action(service, prompt_lower)
        
        return {
            'service': service,
            'action': action,
            'confidence': round(confidence, 2),
            'matched_keywords': info['matched_keywords'],
            'description': info['description'],
            'reasoning': f"Selected {service} based on matching keywords: {', '.join(info['matched_keywords'][:3])}"
        }
    
    def _determine_action(self, service: str, prompt_lower: str) -> str:
        """Determine specific action based on prompt"""
        
        if service == 'redash':
            # Specific phrase matching (longer first)
            if 'data source' in prompt_lower or 'datasource' in prompt_lower:
                return 'list_data_sources'
            elif 'execute query' in prompt_lower or 'run query' in prompt_lower:
                # Extract query ID if present
                import re
                match = re.search(r'query\s+(\d+)', prompt_lower)
                if match:
                    return f'execute_query_{match.group(1)}'
                return 'execute_query'
            elif 'list queries' in prompt_lower or 'show queries' in prompt_lower:
                return 'list_queries'
            elif 'dashboard' in prompt_lower:
                return 'list_dashboards'
            elif 'queries' in prompt_lower:
                return 'list_queries'
            else:
                return 'list_data_sources'  # Default
        
        return 'unknown'
    
    def _is_data_query(self, prompt: str) -> bool:
        """
        Determine if prompt is asking for actual data vs metadata
        
        Data queries: "show me applications", "get all orders", "how many users"
        Metadata queries: "list data sources", "show queries", "list dashboards"
        """
        prompt_lower = prompt.lower()
        
        # Metadata keywords
        metadata_keywords = [
            'list data sources', 'show data sources', 'list datasources',
            'list queries', 'show queries', 'available queries',
            'list dashboards', 'show dashboards', 'available dashboards',
            'what queries', 'what dashboards'
        ]
        
        # Check if it's explicitly a metadata query
        for keyword in metadata_keywords:
            if keyword in prompt_lower:
                return False
        
        # Data query indicators
        data_indicators = [
            'show me', 'give me', 'get all', 'get me', 'find',
            'how many', 'count', 'total', 'sum', 'average',
            'last', 'recent', 'today', 'yesterday', 'this week',
            'approved', 'pending', 'rejected', 'completed',
            'from table', 'in table', 'where', 'with status'
        ]
        
        for indicator in data_indicators:
            if indicator in prompt_lower:
                return True
        
        # If asking about specific table names
        if 'table' in prompt_lower and any(word in prompt_lower for word in ['from', 'in', 'at']):
            return True
        
        return False
    
    async def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Process a user prompt with LLM intelligence:
        1. Detect if it's a data query vs metadata query
        2. For data queries: Use autonomous Text-to-SQL
        3. For metadata queries: Use direct API calls
        4. Return results with natural language answer
        """
        
        logger.info(f"Processing prompt: {prompt}")
        
        # Step 1: Check if this is a data query that needs SQL
        if self._is_data_query(prompt):
            if self.text_to_sql_agent:
                logger.info("🎯 Detected data query - using autonomous Text-to-SQL")
                return await self._handle_data_query(prompt)
            else:
                logger.warning("Text-to-SQL not available, falling back to basic handling")
        
        # Step 2: Basic routing for metadata queries (Redash vs other services)
        analysis = self.analyze_prompt(prompt)
        
        if not analysis['service']:
            return {
                'success': False,
                'error': 'Could not determine which service to use',
                'prompt': prompt,
                'analysis': analysis
            }
        
        service = analysis['service']
        
        # Step 3: Use LLM to understand specific intent
        if service == 'redash':
            if self.bedrock_client:
                logger.info("Using LLM-powered Redash handling")
                return await self._handle_redash_with_llm(prompt, analysis)
            else:
                logger.warning("Bedrock client not available, using basic handling")
                action = analysis['action']
                return await self._handle_redash(action, prompt, analysis)
        else:
            return {
                'success': False,
                'error': f'Service {service} not yet implemented',
                'prompt': prompt,
                'analysis': analysis
            }
    
    async def _handle_data_query(self, prompt: str) -> Dict[str, Any]:
        """
        Handle data queries using autonomous Text-to-SQL
        """
        try:
            # Step 1: Determine which data source to use
            logger.info("Determining data source...")
            
            # Get available data sources
            data_sources = self.redash_client.list_data_sources()
            
            # Check if user specified a data source in the prompt
            prompt_lower = prompt.lower()
            data_source_id = None
            
            # Try to find data source mentioned in prompt
            for ds in data_sources:
                ds_name_lower = ds['name'].lower()
                if ds_name_lower in prompt_lower:
                    data_source_id = ds['id']
                    logger.info(f"User specified data source '{ds['name']}' (ID: {data_source_id})")
                    break
            
            # If not specified, ask LLM
            if not data_source_id:
                logger.info("No explicit data source mentioned, asking LLM...")
                ds_summary = "\n".join([f"- {ds['id']}: {ds['name']}" for ds in data_sources])
                
                ds_prompt = f"""Given this user question and available data sources, which data source should be used?

USER QUESTION: {prompt}

AVAILABLE DATA SOURCES:
{ds_summary}

Respond with ONLY the data source ID number that best matches the question."""

                ds_response = self.bedrock_client.generate_response(ds_prompt, max_tokens=100)
                data_source_id = int(ds_response.strip())
            
            logger.info(f"LLM selected data source ID: {data_source_id}")
            
            # Step 2: Use Text-to-SQL agent to execute query
            result = self.text_to_sql_agent.execute_and_explain(data_source_id, prompt)
            
            return {
                'success': True,
                'service': 'redash',
                'action': 'sql_query',
                'data_source_id': data_source_id,
                'answer': result.get('answer'),
                'sql': result.get('sql'),
                'explanation': result.get('explanation'),
                'row_count': result.get('row_count'),
                'raw_data': result.get('raw_data'),
                'prompt': prompt
            }
            
        except Exception as e:
            logger.error(f"Error in data query handling: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'service': 'redash',
                'action': 'sql_query',
                'prompt': prompt
            }
    
    async def _handle_redash_with_llm(self, prompt: str, analysis: Dict) -> Dict[str, Any]:
        """Handle Redash actions with LLM intelligence"""
        
        if not self.redash_client:
            return {
                'success': False,
                'error': 'Redash client not available',
                'prompt': prompt
            }
        
        if not self.bedrock_client:
            logger.error("Bedrock client is None!")
            return {
                'success': False,
                'error': 'LLM not available',
                'prompt': prompt
            }
        
        try:
            logger.info(f"Processing with LLM: {prompt}")
            # Step 1: Use LLM to understand what to do
            logger.info("Using LLM to analyze intent...")
            intent = self.bedrock_client.analyze_intent(prompt, self.available_actions)
            
            logger.info(f"LLM Intent: {intent}")
            
            action = intent.get('action', 'list_data_sources')
            parameters = intent.get('parameters', {})
            filter_field = intent.get('filter')
            filter_value = intent.get('filter_value')
            
            # Step 2: Fetch data from Redash
            result = None
            
            if action == 'list_data_sources':
                data_sources = self.redash_client.list_data_sources()
                result = {'data_sources': data_sources, 'count': len(data_sources)}
            
            elif action == 'list_queries':
                queries_result = self.redash_client.list_queries()
                result = {
                    'queries': queries_result.get('results', []),
                    'count': queries_result.get('count', 0)
                }
            
            elif action == 'execute_query':
                query_id = parameters.get('query_id')
                if query_id:
                    result = self.redash_client.execute_query(int(query_id))
                else:
                    result = {'error': 'No query_id provided'}
            
            elif action == 'get_query':
                query_id = parameters.get('query_id')
                if query_id:
                    result = self.redash_client.get_query(int(query_id))
                else:
                    result = {'error': 'No query_id provided'}
            
            elif action == 'list_dashboards':
                dashboards_result = self.redash_client.list_dashboards()
                result = {
                    'dashboards': dashboards_result.get('results', []),
                    'count': dashboards_result.get('count', 0)
                }
            
            # Step 3: Apply LLM-suggested filtering if needed
            if filter_field and filter_value and result:
                result = self._apply_filter(result, filter_field, filter_value)
            
            # Step 4: Use LLM to generate natural language answer
            logger.info("Using LLM to generate answer...")
            answer = self.bedrock_client.generate_answer(
                prompt, 
                result,
                context=f"Action taken: {action}. {intent.get('reasoning', '')}"
            )
            
            return {
                'success': True,
                'service': 'redash',
                'action': action,
                'llm_intent': intent,
                'raw_data': result,
                'answer': answer,  # Natural language answer!
                'prompt': prompt,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error in LLM-powered Redash handling: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'service': 'redash',
                'prompt': prompt
            }
    
    def _apply_filter(self, data: Dict, field: str, value: str) -> Dict:
        """Apply filtering to results"""
        try:
            if 'data_sources' in data:
                filtered = [ds for ds in data['data_sources'] 
                           if value.lower() in str(ds.get(field, '')).lower()]
                return {'data_sources': filtered, 'count': len(filtered)}
            elif 'queries' in data:
                filtered = [q for q in data['queries'] 
                           if value.lower() in str(q.get(field, '')).lower()]
                return {'queries': filtered, 'count': len(filtered)}
        except Exception as e:
            logger.error(f"Error filtering: {e}")
        return data
    
    async def _handle_redash(self, action: str, prompt: str, analysis: Dict) -> Dict[str, Any]:
        """Handle Redash actions using direct API"""
        
        if not self.redash_client:
            return {
                'success': False,
                'error': 'Redash client not available',
                'prompt': prompt,
                'analysis': analysis
            }
        
        try:
            result = None
            
            if action == 'list_data_sources':
                data_sources = self.redash_client.list_data_sources()
                result = {
                    'data_sources': data_sources,
                    'count': len(data_sources)
                }
            
            elif action == 'list_queries':
                queries_result = self.redash_client.list_queries()
                result = {
                    'queries': queries_result.get('results', []),
                    'count': queries_result.get('count', 0)
                }
            
            elif action == 'list_dashboards':
                dashboards_result = self.redash_client.list_dashboards()
                result = {
                    'dashboards': dashboards_result.get('results', []),
                    'count': dashboards_result.get('count', 0)
                }
            
            elif action.startswith('execute_query_'):
                query_id = int(action.split('_')[-1])
                result = self.redash_client.execute_query(query_id)
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown Redash action: {action}',
                    'prompt': prompt,
                    'analysis': analysis
                }
            
            return {
                'success': True,
                'service': 'redash',
                'action': action,
                'result': result,
                'prompt': prompt,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error executing Redash action {action}: {e}")
            return {
                'success': False,
                'error': str(e),
                'service': 'redash',
                'action': action,
                'prompt': prompt,
                'analysis': analysis
            }


def get_hybrid_agent() -> SmartAgentHybrid:
    """Get singleton hybrid agent instance"""
    if not hasattr(get_hybrid_agent, 'instance'):
        get_hybrid_agent.instance = SmartAgentHybrid()
    return get_hybrid_agent.instance

