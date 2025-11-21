#!/usr/bin/env python3
"""
Test Smart Agent - Demonstrates intelligent prompt routing
"""

import asyncio
import sys
import logging
from mcp_client import MCPClientManager
from smart_agent import SmartAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example prompts for testing
TEST_PROMPTS = {
    'redash': [
        "Show me all Redash dashboards",
        "List all queries in Redash",
        "Execute query 123 in Redash",
        "Create a new query",
        "List data sources",
        "Show analytics dashboards",
        "Get query details for query 456",
    ],
    'filesystem': [
        "Read file /tmp/example.txt",
        "List files in /home/user",
        "Show directory contents",
        "Write hello world to /tmp/test.txt",
    ],
    'git': [
        "Show git status",
        "Show recent commits",
        "Show git log",
        "What are the latest changes?",
    ],
    'brave-search': [
        "Search web for Model Context Protocol",
        "Find information about Python FastAPI",
        "Look up latest AI news",
        "Search for Redash documentation",
    ],
}


async def test_analyze_prompts():
    """Test the prompt analysis without execution"""
    
    print("\n" + "="*70)
    print(" "*20 + "SMART AGENT - PROMPT ANALYSIS")
    print("="*70 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    agent = SmartAgent(manager)
    
    # Test each category
    for category, prompts in TEST_PROMPTS.items():
        print(f"\n{'='*70}")
        print(f"Category: {category.upper()}")
        print(f"{'='*70}\n")
        
        for prompt in prompts:
            print(f"Prompt: \"{prompt}\"")
            analysis = agent.analyze_prompt(prompt)
            
            print(f"  → Server: {analysis['server_id']}")
            print(f"  → Confidence: {analysis['confidence']}%")
            print(f"  → Tool: {analysis['suggested_tool']}")
            print(f"  → Matched: {', '.join(analysis['matched_keywords'][:3])}")
            print()
    
    print("="*70 + "\n")


async def test_process_single_prompt(prompt: str):
    """Test processing a single prompt end-to-end"""
    
    print("\n" + "="*70)
    print(" "*20 + "SMART AGENT - PROCESS PROMPT")
    print("="*70 + "\n")
    
    print(f"Prompt: \"{prompt}\"\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    agent = SmartAgent(manager)
    
    try:
        result = await agent.process_prompt(prompt)
        
        print("Analysis:")
        print(f"  Server Selected: {result.get('server_id', 'N/A')}")
        print(f"  Confidence: {result.get('analysis', {}).get('confidence', 0)}%")
        print(f"  Tool: {result.get('tool_name', 'N/A')}")
        print()
        
        if result.get('success'):
            print("✅ Success!")
            print(f"Action: {result.get('action')}")
            
            if result.get('result'):
                print(f"Result: {str(result.get('result'))[:200]}...")
            elif result.get('available_tools'):
                print(f"Available Tools: {', '.join(result.get('available_tools', [])[:5])}")
        else:
            print(f"❌ Error: {result.get('error')}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        await manager.shutdown_all_servers()
    
    print("\n" + "="*70 + "\n")


async def test_chat_mode():
    """Test the chat mode with human-readable responses"""
    
    print("\n" + "="*70)
    print(" "*20 + "SMART AGENT - CHAT MODE")
    print("="*70 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    agent = SmartAgent(manager)
    
    test_prompts = [
        "Show me all Redash dashboards",
        "List all queries",
    ]
    
    for prompt in test_prompts:
        print(f"User: {prompt}")
        print()
        
        try:
            response = await agent.chat(prompt)
            print("Agent:")
            for line in response.split('\n'):
                print(f"  {line}")
            print()
        except Exception as e:
            print(f"  Error: {e}")
            print()
    
    await manager.shutdown_all_servers()
    print("="*70 + "\n")


async def interactive_mode():
    """Interactive mode for testing prompts"""
    
    print("\n" + "="*70)
    print(" "*15 + "SMART AGENT - INTERACTIVE MODE")
    print("="*70 + "\n")
    print("Type prompts to test the agent. Type 'quit' to exit.")
    print("Examples:")
    print("  - Show me all Redash dashboards")
    print("  - List all queries")
    print("  - Search web for Python FastAPI")
    print("="*70 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    agent = SmartAgent(manager)
    
    try:
        while True:
            try:
                prompt = input("You: ").strip()
                
                if not prompt:
                    continue
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋\n")
                    break
                
                print()
                
                # Analyze first
                analysis = agent.analyze_prompt(prompt)
                print(f"🤖 Analysis:")
                print(f"   Server: {analysis['server_id']}")
                print(f"   Confidence: {analysis['confidence']}%")
                print(f"   Tool: {analysis['suggested_tool']}")
                print()
                
                # Ask if user wants to execute
                execute = input("Execute? (y/n): ").strip().lower()
                if execute == 'y':
                    print("\n⏳ Processing...")
                    result = await agent.process_prompt(prompt)
                    
                    if result.get('success'):
                        print("\n✅ Success!")
                        if result.get('result'):
                            print(f"Result: {str(result.get('result'))[:300]}...")
                    else:
                        print(f"\n❌ Error: {result.get('error')}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    finally:
        await manager.shutdown_all_servers()


async def demo_all_capabilities():
    """Comprehensive demo of all agent capabilities"""
    
    print("\n" + "="*70)
    print(" "*10 + "SMART AGENT - COMPREHENSIVE DEMO")
    print("="*70 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    agent = SmartAgent(manager)
    
    demos = [
        {
            'title': 'Redash Analytics',
            'prompts': [
                "Show me all Redash dashboards",
                "List queries in Redash",
            ]
        },
        {
            'title': 'File Operations',
            'prompts': [
                "List files in /tmp",
                "Read file /etc/hosts",
            ]
        },
        {
            'title': 'Git Operations',
            'prompts': [
                "Show git status",
                "Show recent commits",
            ]
        },
        {
            'title': 'Web Search',
            'prompts': [
                "Search for Model Context Protocol",
            ]
        },
    ]
    
    for demo in demos:
        print(f"\n{'─'*70}")
        print(f"📋 {demo['title']}")
        print(f"{'─'*70}\n")
        
        for prompt in demo['prompts']:
            print(f"Prompt: \"{prompt}\"")
            
            # Analyze
            analysis = agent.analyze_prompt(prompt)
            print(f"  → {analysis['server_id']} ({analysis['confidence']}% confident)")
            print(f"  → Tool: {analysis['suggested_tool']}")
            print()
        
        await asyncio.sleep(0.5)
    
    await manager.shutdown_all_servers()
    
    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70 + "\n")


async def main():
    """Main test function"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'analyze':
            await test_analyze_prompts()
        
        elif command == 'process':
            if len(sys.argv) > 2:
                prompt = ' '.join(sys.argv[2:])
                await test_process_single_prompt(prompt)
            else:
                print("Usage: python test_smart_agent.py process <prompt>")
        
        elif command == 'chat':
            await test_chat_mode()
        
        elif command == 'interactive':
            await interactive_mode()
        
        elif command == 'demo':
            await demo_all_capabilities()
        
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  analyze     - Analyze all test prompts")
            print("  process     - Process a single prompt")
            print("  chat        - Test chat mode")
            print("  interactive - Interactive testing mode")
            print("  demo        - Comprehensive demo")
    
    else:
        # Default: run comprehensive demo
        await demo_all_capabilities()


if __name__ == "__main__":
    asyncio.run(main())

