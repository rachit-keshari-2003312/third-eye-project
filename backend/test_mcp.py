#!/usr/bin/env python3
"""
Test script for MCP integration
Run this to verify your MCP setup is working correctly
"""

import asyncio
import sys
import logging
from mcp_client import MCPClientManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_integration():
    """Test the MCP client integration"""
    
    print("\n" + "="*60)
    print("Testing MCP Integration")
    print("="*60 + "\n")
    
    # Initialize MCP manager
    print("1. Initializing MCP Manager...")
    manager = MCPClientManager(config_path="../mcp.json")
    
    # Load configuration
    print("2. Loading MCP configuration...")
    success = await manager.load_config()
    if not success:
        print("❌ Failed to load configuration")
        return False
    print("✅ Configuration loaded successfully")
    
    # Get list of configured servers
    print("\n3. Configured MCP Servers:")
    statuses = manager.get_all_servers_status()
    for status in statuses:
        print(f"   - {status['id']}: {status['name']}")
    
    # Test connecting to filesystem server (most likely to work)
    print("\n4. Testing connection to 'filesystem' server...")
    try:
        success = await manager.initialize_server("filesystem")
        if success:
            print("✅ Successfully connected to filesystem server")
            
            # List tools
            print("\n5. Listing available tools on filesystem server...")
            tools = await manager.list_tools("filesystem")
            if tools:
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools[:3]:  # Show first 3 tools
                    tool_name = tool.get('name', 'unknown')
                    tool_desc = tool.get('description', 'No description')
                    print(f"   - {tool_name}: {tool_desc}")
                if len(tools) > 3:
                    print(f"   ... and {len(tools) - 3} more")
            else:
                print("⚠️  No tools found (this might be normal for some servers)")
            
            # List resources
            print("\n6. Listing available resources...")
            try:
                resources = await manager.list_resources("filesystem")
                if resources:
                    print(f"✅ Found {len(resources)} resources")
                else:
                    print("ℹ️  No resources available")
            except Exception as e:
                print(f"ℹ️  Resources not supported or error: {e}")
            
            # Cleanup
            print("\n7. Disconnecting from filesystem server...")
            await manager.shutdown_server("filesystem")
            print("✅ Disconnected successfully")
            
        else:
            print("❌ Failed to connect to filesystem server")
            print("   This might be because:")
            print("   - Node.js is not installed (required for npx)")
            print("   - The MCP server package is not installed")
            print("   - Network issues or permissions")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    
    # Cleanup
    print("\n8. Shutting down MCP manager...")
    await manager.shutdown_all_servers()
    print("✅ All servers shut down")
    
    print("\n" + "="*60)
    print("✅ MCP Integration Test Completed Successfully!")
    print("="*60 + "\n")
    
    print("Next steps:")
    print("1. Start the backend server: python app.py")
    print("2. Test the API: curl http://localhost:8000/api/mcp/servers")
    print("3. Connect to servers via the API")
    print("4. Integrate MCP tools into your agents")
    print()
    
    return True


async def test_specific_server(server_id: str):
    """Test a specific MCP server"""
    
    print(f"\nTesting server: {server_id}")
    print("-" * 40)
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    # Check if server exists
    status = manager.get_server_status(server_id)
    if not status.get('exists', True):
        print(f"❌ Server '{server_id}' not found in configuration")
        return False
    
    print(f"Server: {status['name']}")
    print(f"Command: {status['command']} {' '.join(status['args'])}")
    print(f"Capabilities: {', '.join(status['capabilities'])}")
    
    # Try to connect
    print(f"\nConnecting to {server_id}...")
    try:
        success = await manager.initialize_server(server_id)
        if success:
            print(f"✅ Connected successfully")
            
            # List tools
            tools = await manager.list_tools(server_id)
            print(f"\nAvailable tools: {len(tools)}")
            for tool in tools:
                tool_name = tool.get('name', 'unknown')
                tool_desc = tool.get('description', 'No description')
                print(f"  • {tool_name}: {tool_desc}")
            
            # Cleanup
            await manager.shutdown_server(server_id)
            return True
        else:
            print(f"❌ Failed to connect")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        await manager.shutdown_all_servers()
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific server
        server_id = sys.argv[1]
        asyncio.run(test_specific_server(server_id))
    else:
        # Run full test suite
        success = asyncio.run(test_mcp_integration())
        sys.exit(0 if success else 1)

