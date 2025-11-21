#!/usr/bin/env python3
"""
Smart Agent - Intelligent MCP Router
Analyzes user prompts and routes to appropriate MCP servers
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

# Try to import real client first, fallback to old one
try:
    from mcp_client_real import MCPClientManager
except ImportError:
    from mcp_client import MCPClientManager

logger = logging.getLogger(__name__)


class SmartAgent:
    """
    Intelligent agent that analyzes prompts and routes to appropriate MCP servers
    """
    
    def __init__(self, mcp_manager: MCPClientManager):
        self.mcp = mcp_manager
        self.server_capabilities = {}
        
        # Define keywords and patterns for each MCP server
        self.mcp_patterns = {
            'redash-mcp': {
                'keywords': [
                    'query', 'queries', 'dashboard', 'dashboards', 'visualization',
                    'redash', 'analytics', 'report', 'reports', 'data source',
                    'data sources', 'datasource', 'datasources', 'database',
                    'sql', 'database query', 'chart', 'graph', 'metrics',
                    'kpi', 'execute query', 'run query', 'create query'
                ],
                'patterns': [
                    r'show.*dashboard',
                    r'list.*queries',
                    r'execute.*query',
                    r'run.*query',
                    r'create.*query',
                    r'analytics.*data',
                    r'redash.*',
                ],
                'description': 'Redash analytics and data visualization'
            },
            'filesystem': {
                'keywords': [
                    'file', 'files', 'read file', 'write file', 'directory',
                    'folder', 'list files', 'create file', 'delete file',
                    'save file', 'open file'
                ],
                'patterns': [
                    r'read.*file',
                    r'write.*file',
                    r'list.*files',
                    r'show.*files',
                    r'file.*content',
                ],
                'description': 'File system operations'
            },
            'git': {
                'keywords': [
                    'git', 'commit', 'commits', 'repository', 'repo',
                    'branch', 'branches', 'git log', 'git status',
                    'diff', 'changes', 'version control'
                ],
                'patterns': [
                    r'git\s+(status|log|diff|commit)',
                    r'show.*commits',
                    r'repository.*',
                ],
                'description': 'Git version control operations'
            },
            'brave-search': {
                'keywords': [
                    'search', 'google', 'web search', 'find online',
                    'look up', 'internet', 'browse', 'search web'
                ],
                'patterns': [
                    r'search.*web',
                    r'find.*online',
                    r'look.*up',
                    r'search for',
                ],
                'description': 'Web search using Brave'
            },
            'postgres': {
                'keywords': [
                    'postgres', 'postgresql', 'database', 'table',
                    'sql query', 'select', 'insert', 'update', 'delete'
                ],
                'patterns': [
                    r'postgres.*query',
                    r'database.*query',
                    r'sql\s+select',
                ],
                'description': 'PostgreSQL database operations'
            },
            'slack': {
                'keywords': [
                    'slack', 'message', 'send message', 'notify',
                    'channel', 'team', 'chat'
                ],
                'patterns': [
                    r'send.*slack',
                    r'slack.*message',
                    r'notify.*team',
                ],
                'description': 'Slack messaging'
            },
            'github': {
                'keywords': [
                    'github', 'issue', 'issues', 'pull request', 'pr',
                    'create repo', 'repository'
                ],
                'patterns': [
                    r'github.*issue',
                    r'create.*pr',
                    r'pull.*request',
                ],
                'description': 'GitHub operations'
            },
        }
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze a user prompt and determine which MCP server to use
        
        Returns:
            Dict with 'server_id', 'confidence', 'suggested_tool', 'reasoning'
        """
        prompt_lower = prompt.lower()
        scores = {}
        
        # Score each MCP server based on keyword and pattern matching
        for server_id, config in self.mcp_patterns.items():
            score = 0
            matched_keywords = []
            matched_patterns = []
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword.lower() in prompt_lower:
                    score += 2
                    matched_keywords.append(keyword)
            
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, prompt_lower):
                    score += 3
                    matched_patterns.append(pattern)
            
            if score > 0:
                scores[server_id] = {
                    'score': score,
                    'matched_keywords': matched_keywords,
                    'matched_patterns': matched_patterns,
                    'description': config['description']
                }
        
        # Select the best match
        if not scores:
            return {
                'server_id': None,
                'confidence': 0,
                'suggested_tool': None,
                'reasoning': 'No matching MCP server found for this prompt'
            }
        
        best_match = max(scores.items(), key=lambda x: x[1]['score'])
        server_id = best_match[0]
        info = best_match[1]
        
        # Calculate confidence (0-100)
        max_possible_score = 20  # Reasonable max
        confidence = min(100, (info['score'] / max_possible_score) * 100)
        
        # Suggest a tool based on the server
        suggested_tool = self._suggest_tool(server_id, prompt_lower)
        
        return {
            'server_id': server_id,
            'confidence': round(confidence, 2),
            'suggested_tool': suggested_tool,
            'matched_keywords': info['matched_keywords'],
            'matched_patterns': info['matched_patterns'],
            'description': info['description'],
            'reasoning': f"Selected {server_id} based on matching keywords: {', '.join(info['matched_keywords'][:3])}"
        }
    
    def _suggest_tool(self, server_id: str, prompt_lower: str) -> Optional[str]:
        """Suggest a specific tool based on the prompt"""
        
        # More specific patterns first (longer phrases matched first)
        tool_suggestions = {
            'redash-mcp': {
                # Check specific phrases first (longer to shorter)
                'data source': 'list_data_sources',
                'datasource': 'list_data_sources',
                'execute query': 'execute_query',
                'run query': 'execute_query',
                'create query': 'create_query',
                'list queries': 'list_queries',
                'list dashboards': 'list_dashboards',
                'show dashboards': 'list_dashboards',
                # Then general keywords
                'dashboard': 'list_dashboards',
                'execute': 'execute_query',
                'run': 'execute_query',
                'create': 'create_query',
                'queries': 'list_queries',
            },
            'filesystem': {
                'read': 'read_file',
                'write': 'write_file',
                'list': 'list_directory',
                'show': 'list_directory',
            },
            'git': {
                'status': 'git_status',
                'log': 'git_log',
                'diff': 'git_diff',
                'commit': 'git_commit',
            },
            'brave-search': {
                'search': 'web_search',
                'find': 'web_search',
                'look': 'web_search',
            },
        }
        
        if server_id in tool_suggestions:
            # Sort by keyword length (longer first) to match more specific phrases
            sorted_keywords = sorted(tool_suggestions[server_id].items(), 
                                    key=lambda x: len(x[0]), 
                                    reverse=True)
            for keyword, tool in sorted_keywords:
                if keyword in prompt_lower:
                    return tool
        
        return None
    
    async def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Process a user prompt end-to-end:
        1. Analyze prompt
        2. Connect to appropriate MCP server
        3. Execute the appropriate tool
        4. Return results
        """
        
        logger.info(f"Processing prompt: {prompt}")
        
        # Step 1: Analyze the prompt
        analysis = self.analyze_prompt(prompt)
        
        if not analysis['server_id']:
            return {
                'success': False,
                'error': 'Could not determine which MCP server to use',
                'prompt': prompt,
                'analysis': analysis
            }
        
        server_id = analysis['server_id']
        
        try:
            # Step 2: Connect to MCP server if not already connected
            server = self.mcp.get_server(server_id)
            if not server or not server.is_connected:
                logger.info(f"Connecting to {server_id}...")
                success = await self.mcp.initialize_server(server_id)
                if not success:
                    return {
                        'success': False,
                        'error': f'Failed to connect to {server_id}',
                        'prompt': prompt,
                        'analysis': analysis
                    }
            
            # Step 3: Get available tools
            tools = await self.mcp.list_tools(server_id)
            tool_names = [t.get('name') for t in tools]
            
            # Step 4: Determine tool and arguments
            tool_name = analysis.get('suggested_tool')
            if not tool_name or tool_name not in tool_names:
                # If suggested tool not available, return available tools
                return {
                    'success': True,
                    'action': 'list_tools',
                    'server_id': server_id,
                    'available_tools': tool_names,
                    'prompt': prompt,
                    'analysis': analysis,
                    'message': f'Connected to {server_id}. Please specify which tool to use.'
                }
            
            # Step 5: Extract arguments from prompt (basic implementation)
            arguments = self._extract_arguments(prompt, tool_name, server_id)
            
            # Step 6: Execute the tool
            logger.info(f"Executing {tool_name} on {server_id} with args: {arguments}")
            result = await self.mcp.call_tool(server_id, tool_name, arguments)
            
            return {
                'success': True,
                'action': 'execute_tool',
                'server_id': server_id,
                'tool_name': tool_name,
                'arguments': arguments,
                'result': result,
                'prompt': prompt,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            return {
                'success': False,
                'error': str(e),
                'prompt': prompt,
                'analysis': analysis
            }
    
    def _extract_arguments(self, prompt: str, tool_name: str, server_id: str) -> Dict[str, Any]:
        """
        Extract arguments from the prompt based on the tool
        This is a basic implementation - can be enhanced with NLP
        """
        
        arguments = {}
        prompt_lower = prompt.lower()
        
        # Redash-specific argument extraction
        if server_id == 'redash-mcp':
            if 'list_queries' in tool_name or 'list_dashboards' in tool_name:
                # Extract page number if mentioned
                page_match = re.search(r'page\s+(\d+)', prompt_lower)
                if page_match:
                    arguments['page'] = int(page_match.group(1))
                else:
                    arguments['page'] = 1
                
                # Extract page size if mentioned
                size_match = re.search(r'(\d+)\s+(?:items|results|queries|dashboards)', prompt_lower)
                if size_match:
                    arguments['pageSize'] = int(size_match.group(1))
                else:
                    arguments['pageSize'] = 10
            
            elif 'execute_query' in tool_name:
                # Extract query ID
                id_match = re.search(r'query\s+(?:id\s+)?(\d+)', prompt_lower)
                if id_match:
                    arguments['queryId'] = int(id_match.group(1))
            
            elif 'get_query' in tool_name:
                id_match = re.search(r'query\s+(?:id\s+)?(\d+)', prompt_lower)
                if id_match:
                    arguments['queryId'] = int(id_match.group(1))
        
        # Filesystem-specific argument extraction
        elif server_id == 'filesystem':
            if 'read_file' in tool_name or 'write_file' in tool_name:
                # Extract file path
                path_match = re.search(r'(?:file|path)\s+["\']?([^\s"\']+)["\']?', prompt_lower)
                if path_match:
                    arguments['path'] = path_match.group(1)
        
        # Web search argument extraction
        elif server_id == 'brave-search':
            # Extract search query (everything after "search for" or similar)
            search_patterns = [
                r'search\s+(?:for\s+)?(.+)',
                r'find\s+(?:information\s+(?:about\s+)?)?(.+)',
                r'look\s+up\s+(.+)',
            ]
            for pattern in search_patterns:
                match = re.search(pattern, prompt_lower)
                if match:
                    arguments['query'] = match.group(1).strip()
                    arguments['count'] = 5
                    break
        
        return arguments
    
    async def chat(self, prompt: str) -> str:
        """
        Process a prompt and return a human-readable response
        """
        result = await self.process_prompt(prompt)
        
        if not result['success']:
            return f"❌ Error: {result.get('error', 'Unknown error')}"
        
        analysis = result.get('analysis', {})
        server_id = result.get('server_id')
        
        response_parts = [
            f"🤖 Smart Agent Analysis:",
            f"   Selected: {server_id} ({analysis.get('description', 'N/A')})",
            f"   Confidence: {analysis.get('confidence', 0)}%",
        ]
        
        if result.get('action') == 'list_tools':
            tools = result.get('available_tools', [])
            response_parts.append(f"\n📋 Available tools:")
            for tool in tools[:5]:
                response_parts.append(f"   • {tool}")
            if len(tools) > 5:
                response_parts.append(f"   ... and {len(tools) - 5} more")
        
        elif result.get('action') == 'execute_tool':
            tool_name = result.get('tool_name')
            result_data = result.get('result', {})
            response_parts.append(f"\n✅ Executed: {tool_name}")
            response_parts.append(f"\n📊 Result: {str(result_data)[:200]}...")
        
        return "\n".join(response_parts)


# Singleton instance
_agent_instance = None

def get_agent(mcp_manager: MCPClientManager) -> SmartAgent:
    """Get or create the SmartAgent singleton"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SmartAgent(mcp_manager)
    return _agent_instance

