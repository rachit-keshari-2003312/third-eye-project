#!/usr/bin/env python3
"""
Direct Redash Integration (no MCP needed!)
Works directly with Redash API
"""

import requests
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class RedashClient:
    """Direct Redash API client"""
    
    def __init__(self, url: str, api_key: str):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Authorization": f"Key {api_key}"}
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to Redash API"""
        url = f"{self.url}/api/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def _post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to Redash API"""
        url = f"{self.url}/api/{endpoint}"
        response = requests.post(url, headers=self.headers, json=json_data, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def list_data_sources(self) -> List[Dict[str, Any]]:
        """List all data sources"""
        return self._get("data_sources")
    
    def get_data_source(self, data_source_id: int) -> Dict[str, Any]:
        """Get a specific data source"""
        return self._get(f"data_sources/{data_source_id}")
    
    def list_queries(self, page: int = 1, page_size: int = 25) -> Dict[str, Any]:
        """List all queries"""
        params = {"page": page, "page_size": page_size}
        return self._get("queries", params=params)
    
    def get_query(self, query_id: int) -> Dict[str, Any]:
        """Get a specific query"""
        return self._get(f"queries/{query_id}")
    
    def execute_query(self, query_id: int, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a query"""
        endpoint = f"queries/{query_id}/results"
        if parameters:
            endpoint += f"?{requests.compat.urlencode(parameters)}"
        return self._get(endpoint)
    
    def create_query(self, name: str, data_source_id: int, query: str, 
                    description: str = "", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new query"""
        data = {
            "name": name,
            "data_source_id": data_source_id,
            "query": query,
            "description": description
        }
        if tags:
            data["tags"] = tags
        return self._post("queries", data)
    
    def list_dashboards(self, page: int = 1, page_size: int = 25) -> Dict[str, Any]:
        """List all dashboards"""
        params = {"page": page, "page_size": page_size}
        return self._get("dashboards", params=params)
    
    def get_dashboard(self, dashboard_slug: str) -> Dict[str, Any]:
        """Get a specific dashboard"""
        return self._get(f"dashboards/{dashboard_slug}")


def get_redash_client() -> Optional[RedashClient]:
    """Get configured Redash client"""
    url = os.getenv('REDASH_URL')
    api_key = os.getenv('REDASH_API_KEY')
    
    if not url or not api_key:
        logger.error("REDASH_URL and REDASH_API_KEY must be set")
        return None
    
    return RedashClient(url, api_key)

