from typing import Any

import requests

from settings import MCP_ENDPOINT, MCP_PROTOCOL_VERSION


class MCPClient:
    """Client for MCP server over HTTP"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.endpoint = f"{base_url}{MCP_ENDPOINT}"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        self._tools_cache = []
        self._initialized = False
        self._initialize()

    def _initialize(self) -> bool:
        """Initialize MCP connection with protocol handshake"""
        if self._initialized:
            return True

        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 0,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": MCP_PROTOCOL_VERSION,
                        "capabilities": {},
                        "clientInfo": {"name": "mcp-blender-agent", "version": "1.0.0"},
                    },
                },
                timeout=5,
            )
            if response.ok:
                result = response.json()
                print(
                    f"MCP Protocol: {result.get('result', {}).get('protocolVersion')}"
                )
                self._initialized = True
                return True
            else:
                print(f"Failed to initialize MCP: {response.text}")
                return False
        except Exception as e:
            print(f"Failed to initialize MCP connection: {e}")
            return False

    def list_tools(self) -> list[dict[str, Any]]:
        """List available tools from MCP server"""
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
                timeout=5,
            )

            if response.ok:
                result = response.json()
                self._tools_cache = result.get("result", {}).get("tools", [])
                return self._tools_cache
            else:
                print(f"Error listing tools: {response.text}")
                return []
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            return []

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call a specific tool on the MCP server"""
        response = requests.post(
            self.endpoint,
            headers=self.headers,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            },
            timeout=30,
        )

        if response.ok:
            return response.json().get("result", {})
        else:
            raise Exception(f"Error calling tool {tool_name}: {response.text}")
