#!/usr/bin/env python3
"""
Real MCP Client Implementation
Calls MCP servers via subprocess (no Python SDK needed!)
"""

import subprocess
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)


class MCPServerConnection:
    """Real connection to MCP server via subprocess"""
    
    def __init__(self, server_id: str, command: str, args: List[str], env: Dict[str, str]):
        self.server_id = server_id
        self.command = command
        self.args = args
        self.env = env
        self.process = None
        self.is_connected = False
        self.request_id = 0
    
    async def connect(self) -> bool:
        """Start the MCP server process and initialize it"""
        try:
            logger.info(f"Starting MCP server: {self.server_id}")
            
            # Prepare environment
            full_env = os.environ.copy()
            for key, value in self.env.items():
                # Replace ${VAR_NAME} with actual env values
                if value.startswith("${") and value.endswith("}"):
                    env_var_name = value[2:-1]
                    full_env[key] = os.environ.get(env_var_name, "")
                else:
                    full_env[key] = value
            
            # Start process
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=full_env
            )
            
            # Wait a moment for process to start
            await asyncio.sleep(1)
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "third-eye-backend",
                        "version": "1.0.0"
                    }
                }
            }
            
            request_json = json.dumps(init_request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            
            # Read initialization response
            try:
                response_line = await asyncio.wait_for(
                    self.process.stdout.readline(),
                    timeout=5.0
                )
                if response_line:
                    response = json.loads(response_line.decode())
                    logger.info(f"Initialization response received from {self.server_id}")
                    
                    # Send initialized notification
                    initialized_notification = {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized"
                    }
                    notif_json = json.dumps(initialized_notification) + "\n"
                    self.process.stdin.write(notif_json.encode())
                    await self.process.stdin.drain()
                    logger.info(f"Sent initialized notification to {self.server_id}")
                    
            except asyncio.TimeoutError:
                logger.warning(f"No initialization response from {self.server_id}, continuing anyway")
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in init response: {e}, continuing anyway")
            
            self.is_connected = True
            self.request_id = 1  # Start tool requests from ID 1
            logger.info(f"✅ MCP server {self.server_id} started and initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server {self.server_id}: {e}")
            self.is_connected = False
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self.is_connected or not self.process:
            raise Exception(f"Not connected to {self.server_id}")
        
        try:
            # Increment request ID for each call
            self.request_id += 1
            current_request_id = self.request_id
            
            # Prepare JSON-RPC request
            request = {
                "jsonrpc": "2.0",
                "id": current_request_id,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            logger.info(f"Calling tool {tool_name} on {self.server_id} (request ID: {current_request_id})")
            
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            
            # Read response with timeout
            # MCP servers may send multiple messages (notifications, logs, then the actual result)
            # We need to read until we get the response with matching ID
            try:
                start_time = asyncio.get_event_loop().time()
                timeout = 15.0
                
                while True:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    remaining_timeout = timeout - elapsed
                    
                    if remaining_timeout <= 0:
                        raise asyncio.TimeoutError()
                    
                    response_line = await asyncio.wait_for(
                        self.process.stdout.readline(),
                        timeout=remaining_timeout
                    )
                    
                    if not response_line:
                        raise Exception("Empty response from MCP server")
                    
                    response_text = response_line.decode().strip()
                    
                    try:
                        response = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON line: {response_text[:100]}")
                        continue
                    
                    # Check if this is a notification (no 'id' field or has 'method' field)
                    if "method" in response and "id" not in response:
                        # This is a notification (logging, etc.), skip it
                        logger.debug(f"Received notification: {response.get('method')}")
                        continue
                    
                    # Check if this is our response (matching ID)
                    if "id" in response:
                        if response.get("id") == current_request_id:
                            # This is our response!
                            logger.info(f"Received matching response for request {current_request_id}")
                            
                            if "result" in response:
                                return response["result"]
                            elif "error" in response:
                                error_msg = response["error"].get("message", str(response["error"]))
                                raise Exception(f"MCP Error: {error_msg}")
                            else:
                                # Return the whole response if no explicit result
                                return response
                        else:
                            # Response with different ID, skip it
                            logger.warning(f"Response ID mismatch: expected {current_request_id}, got {response.get('id')}")
                            continue
                    
            except asyncio.TimeoutError:
                raise Exception(f"Timeout waiting for response from {self.server_id} for tool {tool_name}")
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON response: {e}")
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on {self.server_id}: {e}")
            raise
    
    async def disconnect(self):
        """Stop the MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()
            self.process = None
        self.is_connected = False


class MCPClientManager:
    """Manages multiple MCP server connections (Real Implementation)"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "../mcp.json"
        self.servers: Dict[str, MCPServerConnection] = {}
        self.config: Dict[str, Any] = {}
    
    async def load_config(self) -> bool:
        """Load MCP configuration from mcp.json"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"✅ Loaded MCP configuration")
            return True
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            return False
    
    async def initialize_server(self, server_id: str) -> bool:
        """Initialize and start an MCP server"""
        try:
            if server_id not in self.config.get('mcpServers', {}):
                logger.error(f"Server {server_id} not in config")
                return False
            
            server_config = self.config['mcpServers'][server_id]
            
            # Create connection
            connection = MCPServerConnection(
                server_id=server_id,
                command=server_config['command'],
                args=server_config['args'],
                env=server_config.get('env', {})
            )
            
            # Connect
            success = await connection.connect()
            if success:
                self.servers[server_id] = connection
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error initializing {server_id}: {e}")
            return False
    
    async def shutdown_server(self, server_id: str):
        """Shutdown an MCP server"""
        if server_id in self.servers:
            await self.servers[server_id].disconnect()
            del self.servers[server_id]
    
    async def shutdown_all_servers(self):
        """Shutdown all MCP servers"""
        for server_id in list(self.servers.keys()):
            await self.shutdown_server(server_id)
    
    def get_server(self, server_id: str) -> Optional[MCPServerConnection]:
        """Get a server connection"""
        return self.servers.get(server_id)
    
    def get_server_status(self, server_id: str) -> Dict[str, Any]:
        """Get status of a server"""
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
        """Get status of all servers"""
        statuses = []
        for server_id in self.config.get('mcpServers', {}).keys():
            statuses.append(self.get_server_status(server_id))
        return statuses
    
    async def list_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """List available tools for an MCP server"""
        if server_id not in self.config.get('mcpServers', {}):
            return []
        
        # Get capabilities from config (tools are capabilities)
        server_config = self.config['mcpServers'][server_id]
        capabilities = server_config.get('capabilities', [])
        
        # Convert to tool list format
        tools = []
        for capability in capabilities:
            tools.append({
                'name': capability,
                'description': f'{capability} tool from {server_id}'
            })
        
        return tools
    
    async def call_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on an MCP server"""
        connection = self.get_server(server_id)
        if not connection:
            raise Exception(f"Server {server_id} not initialized")
        
        return await connection.call_tool(tool_name, arguments)

