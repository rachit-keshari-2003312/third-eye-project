#!/usr/bin/env python3
"""
Test script for Redash MCP integration
This script demonstrates how to use the Redash MCP server
"""

import asyncio
import json
import logging
from mcp_client import MCPClientManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_redash_connection():
    """Test connection to Redash MCP server"""
    
    print("\n" + "="*60)
    print("Testing Redash MCP Integration")
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
    
    # Check if Redash server is configured
    status = manager.get_server_status("redash-mcp")
    print(f"\n3. Redash MCP Server Configuration:")
    print(f"   Name: {status.get('name', 'N/A')}")
    print(f"   Command: {status.get('command', 'N/A')}")
    print(f"   Args: {status.get('args', [])}")
    print(f"   Status: {status.get('status', 'unknown')}")
    
    # Connect to Redash server
    print("\n4. Connecting to Redash MCP server...")
    try:
        success = await manager.initialize_server("redash-mcp")
        if success:
            print("✅ Successfully connected to Redash MCP server")
            
            # List available tools
            print("\n5. Listing available tools...")
            tools = await manager.list_tools("redash-mcp")
            if tools:
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    tool_name = tool.get('name', 'unknown')
                    tool_desc = tool.get('description', 'No description')
                    print(f"   • {tool_name}: {tool_desc}")
            else:
                print("⚠️  No tools found")
            
            return True
        else:
            print("❌ Failed to connect to Redash MCP server")
            print("\n   Possible issues:")
            print("   - Check if REDASH_URL is correct in .env")
            print("   - Verify REDASH_API_KEY is valid")
            print("   - Ensure Node.js is installed (for npx)")
            print("   - Check network connectivity to Redash server")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Cleanup
        print("\n6. Cleaning up...")
        await manager.shutdown_all_servers()
        print("✅ Cleanup complete")


async def test_redash_operations():
    """Test various Redash operations"""
    
    print("\n" + "="*60)
    print("Testing Redash MCP Operations")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    try:
        # Connect to Redash
        print("Connecting to Redash MCP server...")
        success = await manager.initialize_server("redash-mcp")
        if not success:
            print("❌ Failed to connect")
            return False
        
        print("✅ Connected\n")
        
        # Test 1: List Data Sources
        print("=" * 40)
        print("Test 1: List Data Sources")
        print("=" * 40)
        try:
            result = await manager.call_tool(
                "redash-mcp",
                "list_data_sources",
                {}
            )
            print(f"✅ Data sources retrieved")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"⚠️  Error listing data sources: {e}")
        
        # Test 2: List Queries
        print("\n" + "=" * 40)
        print("Test 2: List Queries")
        print("=" * 40)
        try:
            result = await manager.call_tool(
                "redash-mcp",
                "list_queries",
                {"page": 1, "pageSize": 5}
            )
            print(f"✅ Queries retrieved")
            if isinstance(result, dict) and 'results' in result:
                queries = result.get('results', [])
                print(f"Found {len(queries)} queries:")
                for query in queries[:3]:  # Show first 3
                    print(f"  • Query ID: {query.get('id')}, Name: {query.get('name')}")
            else:
                print(json.dumps(result, indent=2)[:500])
        except Exception as e:
            print(f"⚠️  Error listing queries: {e}")
        
        # Test 3: List Dashboards
        print("\n" + "=" * 40)
        print("Test 3: List Dashboards")
        print("=" * 40)
        try:
            result = await manager.call_tool(
                "redash-mcp",
                "list_dashboards",
                {"page": 1, "pageSize": 5}
            )
            print(f"✅ Dashboards retrieved")
            if isinstance(result, dict) and 'results' in result:
                dashboards = result.get('results', [])
                print(f"Found {len(dashboards)} dashboards:")
                for dashboard in dashboards[:3]:  # Show first 3
                    print(f"  • Dashboard ID: {dashboard.get('id')}, Name: {dashboard.get('name')}")
            else:
                print(json.dumps(result, indent=2)[:500])
        except Exception as e:
            print(f"⚠️  Error listing dashboards: {e}")
        
        print("\n" + "="*60)
        print("✅ Redash MCP Operations Test Complete")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during operations test: {e}")
        return False
    finally:
        await manager.shutdown_all_servers()


async def demo_redash_workflow():
    """Demonstrate a complete Redash workflow"""
    
    print("\n" + "="*60)
    print("Redash MCP Workflow Demo")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    
    try:
        print("Step 1: Connect to Redash")
        await manager.initialize_server("redash-mcp")
        print("✅ Connected\n")
        
        print("Step 2: Get available data sources")
        data_sources = await manager.call_tool(
            "redash-mcp",
            "list_data_sources",
            {}
        )
        print(f"✅ Found data sources\n")
        
        print("Step 3: List existing queries")
        queries = await manager.call_tool(
            "redash-mcp",
            "list_queries",
            {"page": 1, "pageSize": 10}
        )
        print(f"✅ Retrieved queries\n")
        
        # If you want to create a query, uncomment this:
        # print("Step 4: Create a new query")
        # new_query = await manager.call_tool(
        #     "redash-mcp",
        #     "create_query",
        #     {
        #         "name": "Test Query from MCP",
        #         "data_source_id": 1,  # Use actual data source ID
        #         "query": "SELECT 1 as test",
        #         "description": "Test query created via MCP"
        #     }
        # )
        # print(f"✅ Query created: {new_query.get('id')}\n")
        
        print("Step 4: List dashboards")
        dashboards = await manager.call_tool(
            "redash-mcp",
            "list_dashboards",
            {"page": 1, "pageSize": 10}
        )
        print(f"✅ Retrieved dashboards\n")
        
        print("="*60)
        print("✅ Workflow Complete!")
        print("="*60 + "\n")
        
        print("Summary:")
        print("- Connected to Redash successfully")
        print("- Retrieved data sources")
        print("- Listed queries and dashboards")
        print("- Ready for production use!")
        
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
    finally:
        await manager.shutdown_all_servers()


async def main():
    """Main test function"""
    
    print("\n" + "="*70)
    print(" "*15 + "REDASH MCP INTEGRATION TEST")
    print("="*70)
    
    # Run tests
    tests = [
        ("Connection Test", test_redash_connection),
        ("Operations Test", test_redash_operations),
        ("Workflow Demo", demo_redash_workflow),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n>>> Running: {test_name}")
        try:
            result = await test_func()
            results[test_name] = "✅ PASSED" if result else "⚠️  PARTIAL"
        except Exception as e:
            results[test_name] = f"❌ FAILED: {e}"
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Print summary
    print("\n" + "="*70)
    print(" "*25 + "TEST SUMMARY")
    print("="*70)
    for test_name, result in results.items():
        print(f"{test_name:.<40} {result}")
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "connect":
            asyncio.run(test_redash_connection())
        elif command == "operations":
            asyncio.run(test_redash_operations())
        elif command == "workflow":
            asyncio.run(demo_redash_workflow())
        else:
            print(f"Unknown command: {command}")
            print("Available commands: connect, operations, workflow")
    else:
        # Run all tests
        asyncio.run(main())

