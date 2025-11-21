#!/usr/bin/env python3
"""
Redash SQL Executor with Schema Discovery
Autonomous agent that discovers schema and executes ad-hoc SQL queries
"""

import requests
import logging
from typing import Dict, Any, List, Optional
import time

logger = logging.getLogger(__name__)


class RedashSQLExecutor:
    """
    Executes SQL queries on Redash data sources with schema discovery
    """
    
    def __init__(self, redash_url: str, api_key: str):
        self.redash_url = redash_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Authorization": f"Key {api_key}"}
    
    def get_data_source_schema(self, data_source_id: int) -> List[Dict[str, Any]]:
        """
        Get schema (tables) from a data source
        
        Args:
            data_source_id: ID of the data source
            
        Returns:
            List of table names and metadata
        """
        try:
            # Get schema from Redash
            url = f"{self.redash_url}/api/data_sources/{data_source_id}/schema"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            # Schema is wrapped in {"schema": [...]}
            schema = data.get('schema', [])
            logger.info(f"Retrieved schema for data source {data_source_id}: {len(schema)} tables")
            
            return schema
            
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return []
    
    def search_tables(self, data_source_id: int, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for tables matching a term
        
        Args:
            data_source_id: ID of the data source
            search_term: Term to search for in table names
            
        Returns:
            List of matching tables with columns
        """
        schema = self.get_data_source_schema(data_source_id)
        search_lower = search_term.lower()
        
        matching_tables = []
        for table in schema:
            table_name = table.get('name', '')
            if search_lower in table_name.lower():
                matching_tables.append(table)
        
        logger.info(f"Found {len(matching_tables)} tables matching '{search_term}'")
        return matching_tables
    
    def get_table_structure(self, data_source_id: int, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed structure of a specific table
        
        Args:
            data_source_id: ID of the data source
            table_name: Name of the table
            
        Returns:
            Table structure with columns
        """
        schema = self.get_data_source_schema(data_source_id)
        
        for table in schema:
            if table.get('name', '').lower() == table_name.lower():
                logger.info(f"Found table structure for {table_name}")
                return table
        
        logger.warning(f"Table {table_name} not found")
        return None
    
    def execute_adhoc_query(self, data_source_id: int, query: str, 
                           max_wait: int = 30) -> Dict[str, Any]:
        """
        Execute an ad-hoc SQL query without saving it
        
        Args:
            data_source_id: ID of the data source
            query: SQL query to execute
            max_wait: Maximum seconds to wait for results
            
        Returns:
            Query results
        """
        try:
            logger.info(f"Executing ad-hoc query on data source {data_source_id}")
            logger.info(f"SQL: {query}")
            
            # Create a temporary query
            create_url = f"{self.redash_url}/api/queries"
            create_data = {
                "data_source_id": data_source_id,
                "query": query,
                "name": f"Ad-hoc query {int(time.time())}",
                "options": {}
            }
            
            response = requests.post(create_url, headers=self.headers, 
                                    json=create_data, timeout=30)
            response.raise_for_status()
            query_obj = response.json()
            query_id = query_obj['id']
            
            logger.info(f"Created temporary query with ID: {query_id}")
            
            # Execute the query
            exec_url = f"{self.redash_url}/api/queries/{query_id}/refresh"
            response = requests.post(exec_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            job = response.json()['job']
            
            # Poll for results
            start_time = time.time()
            while time.time() - start_time < max_wait:
                job_url = f"{self.redash_url}/api/jobs/{job['id']}"
                response = requests.get(job_url, headers=self.headers, timeout=10)
                job_status = response.json()['job']
                
                if job_status['status'] == 3:  # Success
                    # Get results
                    result_url = f"{self.redash_url}/api/queries/{query_id}/results"
                    response = requests.get(result_url, headers=self.headers, timeout=30)
                    results = response.json()
                    
                    # Clean up - delete temporary query
                    delete_url = f"{self.redash_url}/api/queries/{query_id}"
                    requests.delete(delete_url, headers=self.headers, timeout=10)
                    
                    logger.info(f"Query executed successfully, returned {len(results.get('query_result', {}).get('data', {}).get('rows', []))} rows")
                    return results
                
                elif job_status['status'] == 4:  # Failed
                    error = job_status.get('error', 'Unknown error')
                    logger.error(f"Query failed: {error}")
                    
                    # Clean up
                    delete_url = f"{self.redash_url}/api/queries/{query_id}"
                    requests.delete(delete_url, headers=self.headers, timeout=10)
                    
                    return {
                        "error": error,
                        "query": query
                    }
                
                time.sleep(1)
            
            # Timeout
            logger.error("Query execution timeout")
            return {
                "error": "Query execution timeout",
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error executing ad-hoc query: {e}", exc_info=True)
            return {
                "error": str(e),
                "query": query
            }

