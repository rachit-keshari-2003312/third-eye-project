#!/usr/bin/env python3
"""
Demo: Smart Agent Prompt Analysis (No MCP SDK required)
Shows how the agent analyzes prompts and selects MCP servers
"""

import re
import json


# Simplified version of Smart Agent logic for demo
class SmartAgentDemo:
    """Demo version of Smart Agent for prompt analysis"""
    
    def __init__(self):
        self.mcp_patterns = {
            'redash-mcp': {
                'keywords': [
                    'query', 'queries', 'dashboard', 'dashboards', 'visualization',
                    'redash', 'analytics', 'report', 'reports', 'data source',
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
        }
    
    def analyze_prompt(self, prompt):
        """Analyze a prompt and determine which MCP server to use"""
        prompt_lower = prompt.lower()
        scores = {}
        
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
        
        if not scores:
            return {
                'server_id': None,
                'confidence': 0,
                'reasoning': 'No matching MCP server found'
            }
        
        best_match = max(scores.items(), key=lambda x: x[1]['score'])
        server_id = best_match[0]
        info = best_match[1]
        
        max_possible_score = 20
        confidence = min(100, (info['score'] / max_possible_score) * 100)
        
        return {
            'server_id': server_id,
            'confidence': round(confidence, 2),
            'matched_keywords': info['matched_keywords'],
            'matched_patterns': info['matched_patterns'],
            'description': info['description'],
            'reasoning': f"Selected {server_id} based on matching keywords: {', '.join(info['matched_keywords'][:3])}"
        }


# Test prompts
TEST_PROMPTS = [
    # Redash
    ("Show me all Redash dashboards", "redash-mcp"),
    ("List all queries in Redash", "redash-mcp"),
    ("Execute query 123", "redash-mcp"),
    ("Show analytics data", "redash-mcp"),
    
    # Filesystem
    ("Read file /tmp/example.txt", "filesystem"),
    ("List files in directory", "filesystem"),
    ("Show directory contents", "filesystem"),
    
    # Git
    ("Show git status", "git"),
    ("Show recent commits", "git"),
    ("What are the latest changes?", "git"),
    
    # Web Search
    ("Search web for Python FastAPI", "brave-search"),
    ("Find information about AI", "brave-search"),
    ("Look up Model Context Protocol", "brave-search"),
]


def main():
    print("\n" + "="*80)
    print(" "*25 + "SMART AGENT - DEMO")
    print(" "*20 + "Prompt Analysis & MCP Selection")
    print("="*80 + "\n")
    
    agent = SmartAgentDemo()
    
    # Group by expected server
    current_server = None
    
    for prompt, expected_server in TEST_PROMPTS:
        if expected_server != current_server:
            current_server = expected_server
            print(f"\n{'─'*80}")
            print(f"🎯 Testing: {expected_server.upper()}")
            print(f"{'─'*80}\n")
        
        # Analyze
        result = agent.analyze_prompt(prompt)
        
        # Display
        print(f"Prompt: \"{prompt}\"")
        if result['server_id']:
            print(f"  → Server: {result['server_id']} ({result.get('description', 'N/A')})")
            print(f"  → Confidence: {result['confidence']}%")
        
            keywords_str = ', '.join(result.get('matched_keywords', [])[:3])
            if len(result.get('matched_keywords', [])) > 3:
                keywords_str += f" (+{len(result['matched_keywords']) - 3} more)"
            print(f"  → Matched: {keywords_str}")
            
            # Check if correct
            is_correct = result['server_id'] == expected_server
            status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
            print(f"  → Status: {status}")
        else:
            print(f"  → Server: None (no match)")
            print(f"  → Status: ❌ NO MATCH")
        print()
    
    print("="*80 + "\n")
    
    # Interactive section
    print("🎮 Try your own prompts!")
    print("─"*80)
    print("Examples:")
    print("  • Show me all Redash dashboards")
    print("  • List all queries")
    print("  • Read file /tmp/example.txt")
    print("  • Show git status")
    print("  • Search for Python tutorials")
    print("─"*80 + "\n")
    
    while True:
        try:
            user_prompt = input("Your prompt (or 'quit'): ").strip()
            
            if not user_prompt:
                continue
            
            if user_prompt.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            result = agent.analyze_prompt(user_prompt)
            
            print()
            if result['server_id']:
                print(f"🤖 Analysis:")
                print(f"   Server: {result['server_id']}")
                print(f"   Description: {result['description']}")
                print(f"   Confidence: {result['confidence']}%")
                print(f"   Matched Keywords: {', '.join(result['matched_keywords'][:5])}")
                print(f"   Reasoning: {result['reasoning']}")
            else:
                print("❌ No matching MCP server found")
                print("   Try mentioning: redash, files, git, or search")
            print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()

