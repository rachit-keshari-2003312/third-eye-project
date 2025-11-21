#!/usr/bin/env python3
"""
Test the Text-to-SQL agent step by step
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from bedrock_client import get_bedrock_client
from redash_sql_executor import RedashSQLExecutor
from text_to_sql_agent import TextToSQLAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_text_to_sql():
    # Initialize clients
    bedrock = get_bedrock_client()
    sql_executor = RedashSQLExecutor(
        os.getenv('REDASH_URL'),
        os.getenv('REDASH_API_KEY')
    )
    
    agent = TextToSQLAgent(bedrock, sql_executor)
    
    # Test question
    question = "Give me all the application_id which is approved in last 2 hours from a_application_stage_tracker table"
    
    # Find data source (let's use 90 as identified by the agent)
    data_source_id = 90
    
    print(f"\n{'='*80}")
    print(f"Testing Text-to-SQL Agent")
    print(f"{'='*80}")
    print(f"\nQuestion: {question}")
    print(f"Data Source ID: {data_source_id}")
    
    # Step 1: Get schema
    print(f"\n{'='*80}")
    print(f"Step 1: Getting schema...")
    print(f"{'='*80}")
    schema = sql_executor.get_data_source_schema(data_source_id)
    print(f"Found {len(schema)} tables")
    
    # Search for the table
    matching_tables = [t for t in schema if 'application' in t.get('name', '').lower()]
    print(f"\nTables with 'application' in name:")
    for table in matching_tables[:5]:
        print(f"  - {table.get('name')}")
    
    # Step 2: Discover relevant tables
    print(f"\n{'='*80}")
    print(f"Step 2: Discovering relevant tables...")
    print(f"{'='*80}")
    relevant_tables = agent._discover_relevant_tables(data_source_id, question)
    print(f"LLM identified {len(relevant_tables)} relevant tables:")
    for table in relevant_tables[:5]:
        print(f"  - {table.get('name')}: {len(table.get('columns', []))} columns")
    
    # Step 3: Generate SQL
    print(f"\n{'='*80}")
    print(f"Step 3: Generating SQL...")
    print(f"{'='*80}")
    sql_result = agent.generate_sql(data_source_id, question, schema=relevant_tables)
    
    if 'error' in sql_result:
        print(f"❌ Error: {sql_result['error']}")
    else:
        print(f"✅ SQL Generated:")
        print(f"\n{sql_result.get('sql')}\n")
        print(f"Explanation: {sql_result.get('explanation')}")
    
    print(f"\n{'='*80}")

if __name__ == "__main__":
    test_text_to_sql()

