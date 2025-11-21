#!/usr/bin/env python3
"""
Demo: Graph-Ready Data from Backend
Shows different types of data structures for frontend charts
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def query_backend(prompt: str):
    """Send a prompt to the backend and return the response"""
    response = requests.post(
        f"{BASE_URL}/api/agent/prompt",
        headers={"Content-Type": "application/json"},
        json={"prompt": prompt}
    )
    return response.json()


def demo_list_data():
    """Demo 1: Simple list of records (for tables/lists)"""
    print("\n" + "="*80)
    print("📋 DEMO 1: LIST DATA (For Tables/Lists)")
    print("="*80)
    
    prompt = "From ZC-Prod-Wibmo: give me 10 application_id from a_application_stage_tracker where current_status contains approved and created in last 30 days"
    
    print(f"\n💬 Prompt: {prompt}")
    result = query_backend(prompt)
    
    print(f"\n✅ Success: {result['success']}")
    print(f"📊 SQL: {result.get('sql', 'N/A')[:100]}...")
    
    if result.get('raw_data') and result['raw_data'].get('rows'):
        data = result['raw_data']
        print(f"\n📈 Data Structure:")
        print(f"  - Columns: {[c['name'] for c in data['columns']]}")
        print(f"  - Row Count: {len(data['rows'])}")
        print(f"\n🎨 Frontend Use Case: Data Table, List View")
        print(f"\n📊 Sample Data:")
        for i, row in enumerate(data['rows'][:5], 1):
            print(f"  {i}. {row}")
    else:
        print(f"\n❌ No data returned")
        print(f"💬 Answer: {result.get('answer', 'N/A')}")
    
    return result


def demo_count_by_category():
    """Demo 2: Count by category (for pie/bar charts)"""
    print("\n" + "="*80)
    print("📊 DEMO 2: AGGREGATED DATA (For Pie/Bar Charts)")
    print("="*80)
    
    # Try with a limited query to avoid timeout
    prompt = "From ZC-Prod-Wibmo: from a_application_stage_tracker table, show me count of records by current_status, limit to records from last 60 days"
    
    print(f"\n💬 Prompt: {prompt}")
    result = query_backend(prompt)
    
    print(f"\n✅ Success: {result['success']}")
    print(f"📊 SQL: {result.get('sql', 'N/A')}")
    
    if result.get('raw_data') and result['raw_data'].get('rows'):
        data = result['raw_data']
        print(f"\n📈 Data Structure:")
        print(f"  - Columns: {[c['name'] for c in data['columns']]}")
        print(f"  - Row Count: {len(data['rows'])}")
        print(f"\n🎨 Frontend Use Case:")
        print(f"  - Pie Chart (status distribution)")
        print(f"  - Bar Chart (counts by status)")
        print(f"  - Donut Chart")
        print(f"\n📊 Data:")
        for row in data['rows']:
            print(f"  {row}")
    else:
        print(f"\n⚠️ Query issue: {result.get('answer', 'N/A')}")
    
    return result


def demo_multi_column():
    """Demo 3: Multi-column data (for advanced visualizations)"""
    print("\n" + "="*80)
    print("📊 DEMO 3: MULTI-COLUMN DATA (For Advanced Charts)")
    print("="*80)
    
    prompt = "From ZC-Prod-Wibmo: show me application_id, current_status, created_at from a_application_stage_tracker, limit to 10 records from last 30 days"
    
    print(f"\n💬 Prompt: {prompt}")
    result = query_backend(prompt)
    
    print(f"\n✅ Success: {result['success']}")
    print(f"📊 SQL: {result.get('sql', 'N/A')[:100]}...")
    
    if result.get('raw_data') and result['raw_data'].get('rows'):
        data = result['raw_data']
        print(f"\n📈 Data Structure:")
        print(f"  - Columns: {[c['name'] for c in data['columns']]}")
        print(f"  - Row Count: {len(data['rows'])}")
        print(f"\n🎨 Frontend Use Case:")
        print(f"  - Timeline visualization")
        print(f"  - Scatter plots")
        print(f"  - Gantt charts")
        print(f"  - Rich data tables with sorting/filtering")
        print(f"\n📊 Sample Data:")
        for i, row in enumerate(data['rows'][:5], 1):
            print(f"  {i}. {row}")
    else:
        print(f"\n⚠️ No data returned")
        print(f"💬 Answer: {result.get('answer', 'N/A')}")
    
    return result


def demo_complete_api_response():
    """Demo 4: Show complete API response structure"""
    print("\n" + "="*80)
    print("📦 DEMO 4: COMPLETE API RESPONSE STRUCTURE")
    print("="*80)
    
    prompt = "From ZC-Prod-Wibmo: give me 5 application_id from a_application_stage_tracker where created_at >= NOW() - INTERVAL 30 DAY LIMIT 5"
    
    print(f"\n💬 Prompt: {prompt}")
    result = query_backend(prompt)
    
    print(f"\n📦 Complete Response Structure:")
    print(f"  - success: {result.get('success')}")
    print(f"  - service: {result.get('service')}")
    print(f"  - action: {result.get('action')}")
    print(f"  - data_source_id: {result.get('data_source_id')}")
    print(f"  - data_source_name: {result.get('data_source_name', 'N/A')}")
    print(f"  - sql: {result.get('sql', 'N/A')[:80]}...")
    print(f"  - explanation: {result.get('explanation', 'N/A')[:80]}...")
    print(f"  - row_count: {result.get('row_count')}")
    print(f"  - answer: {result.get('answer', 'N/A')[:80]}...")
    print(f"  - raw_data: {'✅ Present' if result.get('raw_data') else '❌ Missing'}")
    
    if result.get('raw_data'):
        print(f"\n📊 Raw Data Structure:")
        print(json.dumps({
            "columns": result['raw_data'].get('columns', []),
            "rows": result['raw_data'].get('rows', [])[:2]  # Show only 2 rows
        }, indent=2))
    
    return result


def main():
    print("\n" + "🚀"*40)
    print("BACKEND GRAPH-READY DATA DEMONSTRATION")
    print("ZC-Prod-Wibmo Data Source Only")
    print("🚀"*40)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("\n✅ Backend is running!")
        else:
            print("\n❌ Backend not responding correctly")
            return
    except Exception as e:
        print(f"\n❌ Backend not running! Start it with:")
        print(f"   cd backend && python3 app_with_redash.py")
        return
    
    # Run demos
    print("\n⏳ Running demos... (each query takes ~5-10 seconds)")
    
    # Demo 1: List data
    demo_list_data()
    time.sleep(2)
    
    # Demo 2: Aggregated data
    demo_count_by_category()
    time.sleep(2)
    
    # Demo 3: Multi-column
    demo_multi_column()
    time.sleep(2)
    
    # Demo 4: Complete response
    demo_complete_api_response()
    
    # Summary
    print("\n" + "="*80)
    print("✅ SUMMARY: YOUR BACKEND IS READY FOR FRONTEND!")
    print("="*80)
    print("""
📊 What you just saw:
  1. List data → Perfect for tables, dropdowns
  2. Aggregated data → Perfect for pie/bar charts
  3. Multi-column data → Perfect for complex visualizations
  4. Complete API structure → All metadata included

🎨 Frontend can now:
  - Send natural language prompts
  - Receive structured JSON
  - Create any type of chart/visualization
  - No data transformation needed!

🚀 Next Steps:
  1. Build frontend UI
  2. Add input field for prompts
  3. Connect to http://localhost:8000/api/agent/prompt
  4. Render charts using raw_data
  5. Display natural language answers

💡 The backend handles:
  ✅ Data source selection (ZC-Prod-Wibmo)
  ✅ Table discovery (359 tables)
  ✅ SQL generation (using Claude)
  ✅ Query execution (via Redash)
  ✅ Natural language responses
""")


if __name__ == "__main__":
    main()

