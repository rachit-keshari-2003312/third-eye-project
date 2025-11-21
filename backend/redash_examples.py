#!/usr/bin/env python3
"""
Redash MCP Integration Examples
Demonstrates how to use Redash MCP server in your application
"""

import asyncio
import json
import logging
from mcp_client import MCPClientManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_list_all_queries():
    """Example: List all queries in Redash"""
    
    print("\n" + "="*60)
    print("Example: List All Queries")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    await manager.initialize_server("redash-mcp")
    
    try:
        # List queries with pagination
        result = await manager.call_tool(
            "redash-mcp",
            "list_queries",
            {
                "page": 1,
                "pageSize": 20,
                "q": ""  # Optional search query
            }
        )
        
        if isinstance(result, dict):
            queries = result.get('results', [])
            print(f"Found {len(queries)} queries:")
            for query in queries:
                print(f"\nQuery ID: {query.get('id')}")
                print(f"  Name: {query.get('name')}")
                print(f"  Description: {query.get('description', 'N/A')}")
                print(f"  Created by: {query.get('user', {}).get('name', 'Unknown')}")
                print(f"  Updated: {query.get('updated_at')}")
        
    finally:
        await manager.shutdown_server("redash-mcp")


async def example_get_query_details():
    """Example: Get details of a specific query"""
    
    print("\n" + "="*60)
    print("Example: Get Query Details")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    await manager.initialize_server("redash-mcp")
    
    try:
        # First, list queries to get an ID
        queries_result = await manager.call_tool(
            "redash-mcp",
            "list_queries",
            {"page": 1, "pageSize": 1}
        )
        
        if isinstance(queries_result, dict) and queries_result.get('results'):
            query_id = queries_result['results'][0]['id']
            print(f"Getting details for query ID: {query_id}\n")
            
            # Get detailed information about the query
            query_details = await manager.call_tool(
                "redash-mcp",
                "get_query",
                {"queryId": query_id}
            )
            
            print(f"Query Details:")
            print(f"  ID: {query_details.get('id')}")
            print(f"  Name: {query_details.get('name')}")
            print(f"  Description: {query_details.get('description', 'N/A')}")
            print(f"  Query SQL:\n{query_details.get('query', 'N/A')}")
            print(f"  Data Source ID: {query_details.get('data_source_id')}")
            print(f"  Created: {query_details.get('created_at')}")
            print(f"  Updated: {query_details.get('updated_at')}")
        else:
            print("No queries found")
        
    finally:
        await manager.shutdown_server("redash-mcp")


async def example_execute_query():
    """Example: Execute a Redash query"""
    
    print("\n" + "="*60)
    print("Example: Execute Query")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    await manager.initialize_server("redash-mcp")
    
    try:
        # Get first query
        queries_result = await manager.call_tool(
            "redash-mcp",
            "list_queries",
            {"page": 1, "pageSize": 1}
        )
        
        if isinstance(queries_result, dict) and queries_result.get('results'):
            query_id = queries_result['results'][0]['id']
            print(f"Executing query ID: {query_id}\n")
            
            # Execute the query
            result = await manager.call_tool(
                "redash-mcp",
                "execute_query",
                {
                    "queryId": query_id,
                    "parameters": {}  # Add parameters if needed
                }
            )
            
            print("Query execution result:")
            print(json.dumps(result, indent=2)[:500])  # Show first 500 chars
        else:
            print("No queries found to execute")
        
    finally:
        await manager.shutdown_server("redash-mcp")


async def example_create_new_query():
    """Example: Create a new query in Redash"""
    
    print("\n" + "="*60)
    print("Example: Create New Query")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    await manager.initialize_server("redash-mcp")
    
    try:
        # First, get available data sources
        data_sources = await manager.call_tool(
            "redash-mcp",
            "list_data_sources",
            {}
        )
        
        if data_sources:
            # Use first available data source
            data_source_id = data_sources[0].get('id') if isinstance(data_sources, list) else 1
            
            print(f"Creating query with data source ID: {data_source_id}\n")
            
            # Create a new query
            new_query = await manager.call_tool(
                "redash-mcp",
                "create_query",
                {
                    "name": "MCP Test Query",
                    "data_source_id": data_source_id,
                    "query": "SELECT 1 as test_column, 'Hello from MCP' as message",
                    "description": "Test query created via MCP integration",
                    "tags": ["mcp", "automated"]
                }
            )
            
            print("Query created successfully!")
            print(f"  Query ID: {new_query.get('id')}")
            print(f"  Name: {new_query.get('name')}")
            print(f"  URL: {new_query.get('url', 'N/A')}")
        else:
            print("No data sources available")
        
    finally:
        await manager.shutdown_server("redash-mcp")


async def example_list_dashboards():
    """Example: List all dashboards"""
    
    print("\n" + "="*60)
    print("Example: List Dashboards")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    await manager.initialize_server("redash-mcp")
    
    try:
        # List dashboards
        result = await manager.call_tool(
            "redash-mcp",
            "list_dashboards",
            {
                "page": 1,
                "pageSize": 20
            }
        )
        
        if isinstance(result, dict):
            dashboards = result.get('results', [])
            print(f"Found {len(dashboards)} dashboards:")
            for dashboard in dashboards:
                print(f"\nDashboard ID: {dashboard.get('id')}")
                print(f"  Name: {dashboard.get('name')}")
                print(f"  Slug: {dashboard.get('slug', 'N/A')}")
                print(f"  Created by: {dashboard.get('user', {}).get('name', 'Unknown')}")
                print(f"  Created: {dashboard.get('created_at')}")
                print(f"  Updated: {dashboard.get('updated_at')}")
        
    finally:
        await manager.shutdown_server("redash-mcp")


async def example_get_dashboard_details():
    """Example: Get dashboard with widgets"""
    
    print("\n" + "="*60)
    print("Example: Get Dashboard Details")
    print("="*60 + "\n")
    
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    await manager.initialize_server("redash-mcp")
    
    try:
        # First, list dashboards
        dashboards_result = await manager.call_tool(
            "redash-mcp",
            "list_dashboards",
            {"page": 1, "pageSize": 1}
        )
        
        if isinstance(dashboards_result, dict) and dashboards_result.get('results'):
            dashboard_id = dashboards_result['results'][0]['id']
            print(f"Getting details for dashboard ID: {dashboard_id}\n")
            
            # Get dashboard details
            dashboard = await manager.call_tool(
                "redash-mcp",
                "get_dashboard",
                {"dashboardId": dashboard_id}
            )
            
            print("Dashboard Details:")
            print(f"  ID: {dashboard.get('id')}")
            print(f"  Name: {dashboard.get('name')}")
            print(f"  Slug: {dashboard.get('slug')}")
            print(f"  Tags: {dashboard.get('tags', [])}")
            
            widgets = dashboard.get('widgets', [])
            print(f"\n  Widgets: {len(widgets)}")
            for widget in widgets[:5]:  # Show first 5 widgets
                print(f"    - {widget.get('visualization', {}).get('name', 'Unnamed')}")
        else:
            print("No dashboards found")
        
    finally:
        await manager.shutdown_server("redash-mcp")


async def example_analytics_agent():
    """Example: Create an analytics agent using Redash"""
    
    print("\n" + "="*60)
    print("Example: Analytics Agent")
    print("="*60 + "\n")
    
    class RedashAnalyticsAgent:
        """An agent that performs analytics using Redash"""
        
        def __init__(self, manager: MCPClientManager):
            self.manager = manager
            self.server_id = "redash-mcp"
        
        async def get_summary(self):
            """Get summary of Redash instance"""
            print("Collecting Redash summary...")
            
            # Get queries count
            queries = await self.manager.call_tool(
                self.server_id,
                "list_queries",
                {"page": 1, "pageSize": 100}
            )
            queries_count = len(queries.get('results', [])) if isinstance(queries, dict) else 0
            
            # Get dashboards count
            dashboards = await self.manager.call_tool(
                self.server_id,
                "list_dashboards",
                {"page": 1, "pageSize": 100}
            )
            dashboards_count = len(dashboards.get('results', [])) if isinstance(dashboards, dict) else 0
            
            # Get data sources count
            data_sources = await self.manager.call_tool(
                self.server_id,
                "list_data_sources",
                {}
            )
            data_sources_count = len(data_sources) if isinstance(data_sources, list) else 0
            
            summary = {
                "queries": queries_count,
                "dashboards": dashboards_count,
                "data_sources": data_sources_count
            }
            
            return summary
        
        async def search_queries(self, keyword: str):
            """Search for queries by keyword"""
            print(f"Searching for queries with keyword: '{keyword}'...")
            
            result = await self.manager.call_tool(
                self.server_id,
                "list_queries",
                {
                    "page": 1,
                    "pageSize": 50,
                    "q": keyword
                }
            )
            
            if isinstance(result, dict):
                queries = result.get('results', [])
                return [{"id": q.get('id'), "name": q.get('name')} for q in queries]
            return []
        
        async def generate_report(self):
            """Generate a comprehensive report"""
            print("Generating analytics report...\n")
            
            summary = await self.get_summary()
            
            print("="*50)
            print("REDASH ANALYTICS REPORT")
            print("="*50)
            print(f"\nTotal Queries: {summary['queries']}")
            print(f"Total Dashboards: {summary['dashboards']}")
            print(f"Total Data Sources: {summary['data_sources']}")
            print("\n" + "="*50)
            
            return summary
    
    # Use the agent
    manager = MCPClientManager(config_path="../mcp.json")
    await manager.load_config()
    await manager.initialize_server("redash-mcp")
    
    try:
        agent = RedashAnalyticsAgent(manager)
        
        # Generate report
        await agent.generate_report()
        
        # Search for queries
        print("\nSearching for 'user' queries:")
        results = await agent.search_queries("user")
        for query in results[:5]:
            print(f"  - {query['name']} (ID: {query['id']})")
        
    finally:
        await manager.shutdown_server("redash-mcp")


async def main():
    """Run all examples"""
    
    examples = [
        ("List All Queries", example_list_all_queries),
        ("Get Query Details", example_get_query_details),
        ("Execute Query", example_execute_query),
        ("List Dashboards", example_list_dashboards),
        ("Get Dashboard Details", example_get_dashboard_details),
        ("Analytics Agent", example_analytics_agent),
        # ("Create New Query", example_create_new_query),  # Uncomment to test creation
    ]
    
    print("\n" + "="*60)
    print("REDASH MCP INTEGRATION EXAMPLES")
    print("="*60)
    
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\n" + "="*60)
    
    for name, func in examples:
        try:
            print(f"\n\n>>> Running: {name}")
            await func()
            await asyncio.sleep(2)  # Pause between examples
        except Exception as e:
            print(f"❌ Error in '{name}': {e}")
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

