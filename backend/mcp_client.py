#!/usr/bin/env python3
"""
MCP Client Implementation
Handles communication with MCP servers using the Model Context Protocol
"""

import asyncio
import json
import logging
import os
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from contextlib import asynccontextmanager
import signal

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    id: str
    command: str
    args: List[str]
    description: str
    capabilities: List[str]
    env: Dict[str, str]


class MCPServerConnection:
    """Manages a connection to a single MCP server"""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self.process: Optional[subprocess.Popen] = None
        self.read_stream = None
        self.write_stream = None
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Connect to the MCP server"""
        try:
            logger.info(f"Connecting to MCP server: {self.config.id}")
            
            # Resolve environment variables
            env = os.environ.copy()
            for key, value in self.config.env.items():
                # Replace ${VAR_NAME} with actual environment variable values
                if value.startswith("${") and value.endswith("}"):
                    env_var_name = value[2:-1]
                    env[key] = os.environ.get(env_var_name, "")
                else:
                    env[key] = value
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.config.command,
                args=self.config.args,
                env=env
            )
            
            # Connect using stdio
            self.read_stream, self.write_stream = await stdio_client(server_params)
            
            # Initialize session
            async with ClientSession(self.read_stream, self.write_stream) as session:
                self.session = session
                await session.initialize()
                self.is_connected = True
                
                logger.info(f"Successfully connected to MCP server: {self.config.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.config.id}: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
            
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                self.process = None
            
            self.is_connected = False
            logger.info(f"Disconnected from MCP server: {self.config.id}")
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {self.config.id}: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self.is_connected or not self.session:
            raise Exception(f"Not connected to MCP server {self.config.id}")
        
        try:
            logger.info(f"Calling tool {tool_name} on server {self.config.id}")
            result = await self.session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on server {self.config.id}: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools on the MCP server"""
        if not self.is_connected or not self.session:
            raise Exception(f"Not connected to MCP server {self.config.id}")
        
        try:
            tools = await self.session.list_tools()
            return tools.tools if hasattr(tools, 'tools') else []
        except Exception as e:
            logger.error(f"Error listing tools on server {self.config.id}: {e}")
            return []
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources on the MCP server"""
        if not self.is_connected or not self.session:
            raise Exception(f"Not connected to MCP server {self.config.id}")
        
        try:
            resources = await self.session.list_resources()
            return resources.resources if hasattr(resources, 'resources') else []
        except Exception as e:
            logger.error(f"Error listing resources on server {self.config.id}: {e}")
            return []
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the MCP server"""
        if not self.is_connected or not self.session:
            raise Exception(f"Not connected to MCP server {self.config.id}")
        
        try:
            result = await self.session.read_resource(uri)
            return result
        except Exception as e:
            logger.error(f"Error reading resource {uri} on server {self.config.id}: {e}")
            raise


class MCPClientManager:
    """Manages multiple MCP server connections"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "mcp.json"
        self.servers: Dict[str, MCPServerConnection] = {}
        self.config: Dict[str, Any] = {}
        
    async def load_config(self) -> bool:
        """Load MCP server configurations from mcp.json"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            logger.info(f"Loaded MCP configuration from {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load MCP configuration: {e}")
            return False
    
    async def initialize_server(self, server_id: str) -> bool:
        """Initialize a specific MCP server"""
        try:
            if server_id not in self.config.get('mcpServers', {}):
                logger.error(f"Server {server_id} not found in configuration")
                return False
            
            server_config_dict = self.config['mcpServers'][server_id]
            
            # Create server configuration
            server_config = MCPServerConfig(
                id=server_id,
                command=server_config_dict['command'],
                args=server_config_dict['args'],
                description=server_config_dict['description'],
                capabilities=server_config_dict.get('capabilities', []),
                env=server_config_dict.get('env', {})
            )
            
            # Create connection
            connection = MCPServerConnection(server_config)
            
            # Connect to server
            success = await connection.connect()
            
            if success:
                self.servers[server_id] = connection
                logger.info(f"Initialized MCP server: {server_id}")
                return True
            else:
                logger.error(f"Failed to connect to MCP server: {server_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing MCP server {server_id}: {e}")
            return False
    
    async def initialize_all_servers(self) -> Dict[str, bool]:
        """Initialize all MCP servers from configuration"""
        results = {}
        
        for server_id in self.config.get('mcpServers', {}).keys():
            try:
                success = await self.initialize_server(server_id)
                results[server_id] = success
            except Exception as e:
                logger.error(f"Error initializing server {server_id}: {e}")
                results[server_id] = False
        
        return results
    
    async def shutdown_server(self, server_id: str):
        """Shutdown a specific MCP server"""
        if server_id in self.servers:
            await self.servers[server_id].disconnect()
            del self.servers[server_id]
            logger.info(f"Shutdown MCP server: {server_id}")
    
    async def shutdown_all_servers(self):
        """Shutdown all MCP servers"""
        for server_id in list(self.servers.keys()):
            await self.shutdown_server(server_id)
        logger.info("All MCP servers shutdown")
    
    def get_server(self, server_id: str) -> Optional[MCPServerConnection]:
        """Get a specific MCP server connection"""
        return self.servers.get(server_id)
    
    def get_all_servers(self) -> Dict[str, MCPServerConnection]:
        """Get all MCP server connections"""
        return self.servers
    
    def get_server_status(self, server_id: str) -> Dict[str, Any]:
        """Get status of a specific server"""
        if server_id not in self.config.get('mcpServers', {}):
            return {
                "id": server_id,
                "exists": False,
                "status": "not_found"
            }
        
        server_config = self.config['mcpServers'][server_id]
        connection = self.servers.get(server_id)
        
        return {
            "id": server_id,
            "name": server_config.get('description', server_id),
            "command": server_config['command'],
            "args": server_config['args'],
            "capabilities": server_config.get('capabilities', []),
            "status": "connected" if (connection and connection.is_connected) else "disconnected",
            "is_initialized": server_id in self.servers
        }
    
    def get_all_servers_status(self) -> List[Dict[str, Any]]:
        """Get status of all configured servers"""
        statuses = []
        for server_id in self.config.get('mcpServers', {}).keys():
            statuses.append(self.get_server_status(server_id))
        return statuses
    
    async def call_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on a specific MCP server"""
        connection = self.get_server(server_id)
        if not connection:
            raise Exception(f"Server {server_id} not initialized")
        
        return await connection.call_tool(tool_name, arguments)
    
    async def list_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """List tools available on a specific server"""
        connection = self.get_server(server_id)
        if not connection:
            raise Exception(f"Server {server_id} not initialized")
        
        return await connection.list_tools()
    
    async def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all tools from all connected servers"""
        all_tools = {}
        for server_id, connection in self.servers.items():
            try:
                tools = await connection.list_tools()
                all_tools[server_id] = tools
            except Exception as e:
                logger.error(f"Error listing tools for server {server_id}: {e}")
                all_tools[server_id] = []
        return all_tools
    
    async def list_resources(self, server_id: str) -> List[Dict[str, Any]]:
        """List resources available on a specific server"""
        connection = self.get_server(server_id)
        if not connection:
            raise Exception(f"Server {server_id} not initialized")
        
        return await connection.list_resources()
    
    async def read_resource(self, server_id: str, uri: str) -> Dict[str, Any]:
        """Read a resource from a specific server"""
        connection = self.get_server(server_id)
        if not connection:
            raise Exception(f"Server {server_id} not initialized")
        
        return await connection.read_resource(uri)

