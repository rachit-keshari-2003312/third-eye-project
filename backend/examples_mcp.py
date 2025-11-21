#!/usr/bin/env python3
"""
Examples of using MCP integration in your application
These examples show how to interact with MCP servers programmatically
"""

import asyncio
import logging
from mcp_client import MCPClientManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_filesystem_operations():
    """Example: Working with filesystem MCP server"""
    
    print("\n" + "="*60)
    print("Example: Filesystem Operations")
    print("="*60 + "\n")
    
    # Initialize manager
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    # Connect to filesystem server
    await manager.initialize_server("filesystem")
    
    # List available tools
    tools = await manager.list_tools("filesystem")
    print(f"Filesystem tools: {[t.get('name') for t in tools]}\n")
    
    # Example: Read a file
    try:
        result = await manager.call_tool(
            "filesystem",
            "read_file",
            {"path": "/tmp/example.txt"}
        )
        print(f"File content: {result}")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    # Cleanup
    await manager.shutdown_server("filesystem")


async def example_git_operations():
    """Example: Working with Git MCP server"""
    
    print("\n" + "="*60)
    print("Example: Git Operations")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    # Connect to git server
    await manager.initialize_server("git")
    
    # Get git status
    try:
        result = await manager.call_tool(
            "git",
            "git_status",
            {}
        )
        print(f"Git status: {result}")
    except Exception as e:
        print(f"Error getting git status: {e}")
    
    # Get git log
    try:
        result = await manager.call_tool(
            "git",
            "git_log",
            {"limit": 5}
        )
        print(f"Recent commits: {result}")
    except Exception as e:
        print(f"Error getting git log: {e}")
    
    await manager.shutdown_server("git")


async def example_database_operations():
    """Example: Working with PostgreSQL MCP server"""
    
    print("\n" + "="*60)
    print("Example: Database Operations")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    # Connect to postgres server
    await manager.initialize_server("postgres")
    
    # List tables
    try:
        result = await manager.call_tool(
            "postgres",
            "list_tables",
            {}
        )
        print(f"Tables: {result}")
    except Exception as e:
        print(f"Error listing tables: {e}")
    
    # Execute query
    try:
        result = await manager.call_tool(
            "postgres",
            "query",
            {"sql": "SELECT * FROM users LIMIT 5"}
        )
        print(f"Query result: {result}")
    except Exception as e:
        print(f"Error executing query: {e}")
    
    await manager.shutdown_server("postgres")


async def example_web_search():
    """Example: Using Brave Search MCP server"""
    
    print("\n" + "="*60)
    print("Example: Web Search")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    # Connect to brave-search server
    await manager.initialize_server("brave-search")
    
    # Perform web search
    try:
        result = await manager.call_tool(
            "brave-search",
            "web_search",
            {"query": "Model Context Protocol", "count": 5}
        )
        print(f"Search results: {result}")
    except Exception as e:
        print(f"Error searching: {e}")
    
    await manager.shutdown_server("brave-search")


async def example_multi_server_workflow():
    """Example: Using multiple MCP servers together"""
    
    print("\n" + "="*60)
    print("Example: Multi-Server Workflow")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    # Initialize multiple servers
    print("Initializing servers...")
    await manager.initialize_server("filesystem")
    await manager.initialize_server("git")
    
    # Get all available tools
    all_tools = await manager.list_all_tools()
    print(f"\nTotal tools available:")
    for server_id, tools in all_tools.items():
        print(f"  {server_id}: {len(tools)} tools")
    
    # Example workflow: Check git status, then read a file
    print("\n--- Workflow: Check repo status and read a file ---")
    
    # Step 1: Get git status
    try:
        git_status = await manager.call_tool("git", "git_status", {})
        print(f"1. Git status: {git_status}")
    except Exception as e:
        print(f"1. Error: {e}")
    
    # Step 2: Read README
    try:
        readme = await manager.call_tool(
            "filesystem",
            "read_file",
            {"path": "./README.md"}
        )
        print(f"2. README length: {len(str(readme))} chars")
    except Exception as e:
        print(f"2. Error: {e}")
    
    # Cleanup
    await manager.shutdown_all_servers()


async def example_error_handling():
    """Example: Proper error handling with MCP servers"""
    
    print("\n" + "="*60)
    print("Example: Error Handling")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    # Try to connect to a server that might not be configured
    try:
        success = await manager.initialize_server("filesystem")
        if success:
            print("✅ Server connected")
            
            # Try to call a tool that might not exist
            try:
                result = await manager.call_tool(
                    "filesystem",
                    "nonexistent_tool",
                    {}
                )
                print(f"Result: {result}")
            except Exception as e:
                print(f"⚠️  Tool call failed (expected): {e}")
            
            await manager.shutdown_server("filesystem")
        else:
            print("❌ Server connection failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Always cleanup
    await manager.shutdown_all_servers()


async def example_agent_with_mcp():
    """Example: Creating an agent that uses MCP tools"""
    
    print("\n" + "="*60)
    print("Example: Agent with MCP Integration")
    print("="*60 + "\n")
    
    class SimpleAgent:
        """A simple agent that can use MCP tools"""
        
        def __init__(self, name: str, mcp_manager: MCPClientManager):
            self.name = name
            self.mcp = mcp_manager
            self.available_tools = {}
        
        async def initialize(self, servers: list):
            """Initialize agent with specific MCP servers"""
            print(f"Initializing agent '{self.name}' with servers: {servers}")
            
            for server_id in servers:
                try:
                    success = await self.mcp.initialize_server(server_id)
                    if success:
                        tools = await self.mcp.list_tools(server_id)
                        self.available_tools[server_id] = [t.get('name') for t in tools]
                        print(f"  ✅ Connected to {server_id}: {len(tools)} tools")
                except Exception as e:
                    print(f"  ❌ Failed to connect to {server_id}: {e}")
        
        async def execute_task(self, task_description: str):
            """Execute a task using available MCP tools"""
            print(f"\n{self.name} is executing: {task_description}")
            
            # Example: Simple task routing
            if "file" in task_description.lower():
                return await self._handle_file_task(task_description)
            elif "git" in task_description.lower():
                return await self._handle_git_task(task_description)
            else:
                return "Task type not recognized"
        
        async def _handle_file_task(self, task):
            """Handle file-related tasks"""
            if "filesystem" in self.available_tools:
                try:
                    result = await self.mcp.call_tool(
                        "filesystem",
                        "list_directory",
                        {"path": "/tmp"}
                    )
                    return f"Listed directory: {result}"
                except Exception as e:
                    return f"Error: {e}"
            return "Filesystem tools not available"
        
        async def _handle_git_task(self, task):
            """Handle git-related tasks"""
            if "git" in self.available_tools:
                try:
                    result = await self.mcp.call_tool(
                        "git",
                        "git_status",
                        {}
                    )
                    return f"Git status: {result}"
                except Exception as e:
                    return f"Error: {e}"
            return "Git tools not available"
        
        async def shutdown(self):
            """Cleanup agent resources"""
            print(f"\nShutting down agent '{self.name}'")
            # Manager shutdown handled by main application
    
    # Create and use agent
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    agent = SimpleAgent("FileSystemAgent", manager)
    await agent.initialize(["filesystem", "git"])
    
    # Execute tasks
    result1 = await agent.execute_task("List files in directory")
    print(f"Result: {result1}")
    
    result2 = await agent.execute_task("Check git status")
    print(f"Result: {result2}")
    
    await agent.shutdown()
    await manager.shutdown_all_servers()


async def main():
    """Run all examples"""
    
    examples = [
        ("Filesystem Operations", example_filesystem_operations),
        ("Git Operations", example_git_operations),
        ("Database Operations", example_database_operations),
        ("Web Search", example_web_search),
        ("Multi-Server Workflow", example_multi_server_workflow),
        ("Error Handling", example_error_handling),
        ("Agent with MCP", example_agent_with_mcp),
    ]
    
    print("\n" + "="*60)
    print("MCP Integration Examples")
    print("="*60)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\n" + "="*60)
    print("Running examples...")
    print("="*60)
    
    # Run each example
    for name, func in examples:
        try:
            await func()
        except Exception as e:
            print(f"\n❌ Example '{name}' failed: {e}\n")
        
        # Pause between examples
        await asyncio.sleep(1)
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
    
    # Or run a specific example:
    # asyncio.run(example_filesystem_operations())
    # asyncio.run(example_agent_with_mcp())

