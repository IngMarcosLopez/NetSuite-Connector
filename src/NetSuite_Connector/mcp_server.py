"""
NetSuite MCP Server - Sample Implementation
Exposes NetSuite operations as MCP tools for AI assistants
"""
import json
import sys
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .NetSuite import NetSuite, NetsuiteObject
from .ODBC import ODBC


@dataclass
class MCPTool:
    """Definition of an MCP tool"""
    name: str
    description: str
    input_schema: dict
    handler: Callable


class NetSuiteMCPServer:
    """
    MCP Server that wraps NetSuite operations as AI-callable tools.
    
    Usage:
        server = NetSuiteMCPServer(
            account_id="123456_SB1",
            consumer_keys={"consumer_key": "xxx", "consumer_secret": "yyy"},
            token_keys={"token_key": "aaa", "token_secret": "bbb"}
        )
        
        # List available tools
        tools = server.list_tools()
        
        # Call a tool
        result = server.call_tool("query_netsuite", {"query": "SELECT TOP 10 * FROM customer"})
    """
    
    def __init__(
        self,
        account_id: Any,
        consumer_keys: dict,
        token_keys: dict
    ):
        self.netsuite = NetSuite(account_id, consumer_keys, token_keys)
        self.odbc = ODBC(account_id, consumer_keys, token_keys)
        self._tools = self._register_tools()
    
    def _register_tools(self) -> dict[str, MCPTool]:
        """Register all available MCP tools"""
        return {
            "query_netsuite": MCPTool(
                name="query_netsuite",
                description="Execute a SuiteQL query against NetSuite. Returns query results as JSON.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SuiteQL query to execute (e.g., 'SELECT TOP 10 * FROM customer')"
                        }
                    },
                    "required": ["query"]
                },
                handler=self._handle_query
            ),
            "call_restlet": MCPTool(
                name="call_restlet",
                description="Call a NetSuite RESTlet endpoint with specified method and data.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Full RESTlet URL"
                        },
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE"],
                            "description": "HTTP method"
                        },
                        "body": {
                            "type": "object",
                            "description": "Request body (for POST/PUT)"
                        }
                    },
                    "required": ["url", "method"]
                },
                handler=self._handle_restlet
            ),
            "get_record": MCPTool(
                name="get_record",
                description="Retrieve a NetSuite record by type and internal ID.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "record_type": {
                            "type": "string",
                            "description": "NetSuite record type (e.g., 'customer', 'salesorder', 'invoice')"
                        },
                        "record_id": {
                            "type": "string",
                            "description": "Internal ID of the record"
                        }
                    },
                    "required": ["record_type", "record_id"]
                },
                handler=self._handle_get_record
            ),
        }
    
    def _handle_query(self, params: dict) -> dict:
        """Execute SuiteQL query"""
        query = params.get("query", "")
        result = self.odbc.query(query)
        return self._format_response(result)
    
    def _handle_restlet(self, params: dict) -> dict:
        """Call RESTlet endpoint"""
        url = params.get("url")
        method = params.get("method", "GET").upper()
        body = params.get("body")
        headers = {"Content-Type": "application/json"}
        
        method_map = {
            "GET": self.netsuite.get,
            "POST": self.netsuite.post,
            "PUT": self.netsuite.put,
            "DELETE": self.netsuite.delete
        }
        
        handler = method_map.get(method)
        if not handler:
            return {"error": f"Unsupported method: {method}"}
        
        kwargs = {"url": url, "headers": headers}
        if body and method in ("POST", "PUT"):
            kwargs["body"] = body
        
        result = handler(**kwargs)
        return self._format_response(result)
    
    def _handle_get_record(self, params: dict) -> dict:
        """Get record via REST Web Services"""
        record_type = params.get("record_type")
        record_id = params.get("record_id")
        account_id = str(self.netsuite.account_id).lower().replace("_", "-")
        
        url = f"https://{account_id}.suitetalk.api.netsuite.com/services/rest/record/v1/{record_type}/{record_id}"
        result = self.netsuite.get(url=url, headers={"Content-Type": "application/json"})
        return self._format_response(result)
    
    def _format_response(self, result: NetsuiteObject) -> dict:
        """Format NetsuiteObject as MCP response"""
        try:
            response_data = json.loads(result.response) if result.response else None
        except json.JSONDecodeError:
            response_data = result.response
        
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "status_code": result.code,
                    "data": response_data
                }, indent=2)
            }],
            "isError": result.code >= 400 if result.code else True
        }
    
    def list_tools(self) -> list[dict]:
        """Return list of available tools in MCP format"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self._tools.values()
        ]
    
    def call_tool(self, name: str, arguments: dict) -> dict:
        """Execute a tool by name with given arguments"""
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Unknown tool: {name}"}
        
        try:
            return tool.handler(arguments)
        except Exception as e:
            return {"error": str(e), "isError": True}
    
    def handle_mcp_request(self, request: dict) -> dict:
        """
        Handle incoming MCP JSON-RPC request.
        This is the main entry point for MCP protocol messages.
        """
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "tools/list":
            result = {"tools": self.list_tools()}
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            result = self.call_tool(tool_name, tool_args)
        elif method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "netsuite-connector-mcp",
                    "version": "0.1.0"
                }
            }
        else:
            result = {"error": f"Unknown method: {method}"}
        
        return {"jsonrpc": "2.0", "id": request_id, "result": result}


def run_stdio_server(
    account_id: str,
    consumer_keys: dict,
    token_keys: dict
):
    """
    Run MCP server using stdio transport (for Claude Desktop integration).
    Reads JSON-RPC requests from stdin, writes responses to stdout.
    """
    server = NetSuiteMCPServer(account_id, consumer_keys, token_keys)
    
    print("NetSuite MCP Server started (stdio mode)", file=sys.stderr)
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_mcp_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": f"Parse error: {e}"}
            }
            print(json.dumps(error_response), flush=True)
