"""
NetSuite MCP Server
Exposes NetSuite operations as MCP tools for AI assistants.
"""
import json
import sys
from typing import Any, Optional

from .NetSuite import NetSuite
from .ODBC import ODBC
from .mcp_config import NetSuiteConfig, load_config_from_env
from .mcp_tools import MCPToolHandler, get_tool_definitions


class NetSuiteMCPServer:
    """
    MCP Server that wraps NetSuite operations as AI-callable tools.
    
    Usage:
        # Option 1: Direct credentials
        server = NetSuiteMCPServer(
            account_id="123456_SB1",
            consumer_keys={"consumer_key": "xxx", "consumer_secret": "yyy"},
            token_keys={"token_key": "aaa", "token_secret": "bbb"}
        )
        
        # Option 2: From config object
        config = load_config_from_env()
        server = NetSuiteMCPServer.from_config(config)
        
        # List available tools
        tools = server.list_tools()
        
        # Call a tool
        result = server.call_tool("query_netsuite", {"query": "SELECT TOP 10 * FROM customer"})
    """
    
    VERSION = "0.1.0"
    PROTOCOL_VERSION = "2024-11-05"
    
    def __init__(
        self,
        account_id: Any,
        consumer_keys: dict,
        token_keys: dict
    ):
        self.netsuite = NetSuite(account_id, consumer_keys, token_keys)
        self.odbc = ODBC(account_id, consumer_keys, token_keys)
        self.tool_handler = MCPToolHandler(self.netsuite, self.odbc)
    
    @classmethod
    def from_config(cls, config: NetSuiteConfig) -> "NetSuiteMCPServer":
        """Create server from NetSuiteConfig object."""
        return cls(
            account_id=config.account_id,
            consumer_keys=config.consumer_keys,
            token_keys=config.token_keys
        )
    
    @classmethod
    def from_env(cls) -> "NetSuiteMCPServer":
        """Create server from environment variables."""
        config = load_config_from_env()
        return cls.from_config(config)
    
    def list_tools(self) -> list[dict]:
        """Return list of available tools in MCP format."""
        return get_tool_definitions()
    
    def call_tool(self, name: str, arguments: dict) -> dict:
        """Execute a tool by name with given arguments."""
        return self.tool_handler.call_tool(name, arguments)
    
    def handle_mcp_request(self, request: dict) -> dict:
        """
        Handle incoming MCP JSON-RPC request.
        This is the main entry point for MCP protocol messages.
        """
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        
        result: Optional[dict] = None
        error: Optional[dict] = None
        
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": self.PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "netsuite-connector-mcp",
                        "version": self.VERSION
                    }
                }
            elif method == "notifications/initialized":
                result = {}
            elif method == "tools/list":
                result = {"tools": self.list_tools()}
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result = self.call_tool(tool_name, tool_args)
            elif method == "ping":
                result = {"pong": True}
            else:
                error = {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
        except Exception as e:
            error = {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        
        response = {"jsonrpc": "2.0", "id": request_id}
        if error:
            response["error"] = error
        else:
            response["result"] = result
        
        return response


def run_stdio_server(
    account_id: Optional[str] = None,
    consumer_keys: Optional[dict] = None,
    token_keys: Optional[dict] = None
):
    """
    Run MCP server using stdio transport (for Claude Desktop integration).
    Reads JSON-RPC requests from stdin, writes responses to stdout.
    
    If credentials are not provided, loads from environment variables.
    """
    if account_id and consumer_keys and token_keys:
        server = NetSuiteMCPServer(account_id, consumer_keys, token_keys)
    else:
        server = NetSuiteMCPServer.from_env()
    
    print("NetSuite MCP Server started (stdio mode)", file=sys.stderr)
    print(f"Version: {NetSuiteMCPServer.VERSION}", file=sys.stderr)
    print(f"Available tools: {len(server.list_tools())}", file=sys.stderr)
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            request = json.loads(line)
            response = server.handle_mcp_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e}"}
            }
            print(json.dumps(error_response), flush=True)
