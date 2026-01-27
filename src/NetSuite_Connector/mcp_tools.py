"""
MCP Tools Module
Defines all available tools for the NetSuite MCP Server.
"""
import json
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .NetSuite import NetSuite, NetsuiteObject
from .ODBC import ODBC


@dataclass
class MCPTool:
    """Definition of an MCP tool."""
    name: str
    description: str
    input_schema: dict
    handler: Optional[Callable] = None


TOOL_SCHEMAS = {
    "query_netsuite": MCPTool(
        name="query_netsuite",
        description="Execute a SuiteQL query against NetSuite. Returns query results as JSON.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SuiteQL query to execute (e.g., 'SELECT TOP 10 id, companyname FROM customer')"
                }
            },
            "required": ["query"]
        }
    ),
    "get_record": MCPTool(
        name="get_record",
        description="Retrieve a NetSuite record by type and internal ID using REST Web Services.",
        input_schema={
            "type": "object",
            "properties": {
                "record_type": {
                    "type": "string",
                    "description": "NetSuite record type (e.g., 'customer', 'salesorder', 'invoice', 'item')"
                },
                "record_id": {
                    "type": "string",
                    "description": "Internal ID of the record to retrieve"
                },
                "expand_sub_resources": {
                    "type": "boolean",
                    "description": "Whether to expand sublists and related records",
                    "default": False
                }
            },
            "required": ["record_type", "record_id"]
        }
    ),
    "create_record": MCPTool(
        name="create_record",
        description="Create a new NetSuite record using REST Web Services.",
        input_schema={
            "type": "object",
            "properties": {
                "record_type": {
                    "type": "string",
                    "description": "NetSuite record type (e.g., 'customer', 'salesorder', 'invoice')"
                },
                "data": {
                    "type": "object",
                    "description": "Record field values as key-value pairs"
                }
            },
            "required": ["record_type", "data"]
        }
    ),
    "update_record": MCPTool(
        name="update_record",
        description="Update an existing NetSuite record using REST Web Services.",
        input_schema={
            "type": "object",
            "properties": {
                "record_type": {
                    "type": "string",
                    "description": "NetSuite record type"
                },
                "record_id": {
                    "type": "string",
                    "description": "Internal ID of the record to update"
                },
                "data": {
                    "type": "object",
                    "description": "Field values to update"
                }
            },
            "required": ["record_type", "record_id", "data"]
        }
    ),
    "delete_record": MCPTool(
        name="delete_record",
        description="Delete a NetSuite record using REST Web Services.",
        input_schema={
            "type": "object",
            "properties": {
                "record_type": {
                    "type": "string",
                    "description": "NetSuite record type"
                },
                "record_id": {
                    "type": "string",
                    "description": "Internal ID of the record to delete"
                }
            },
            "required": ["record_type", "record_id"]
        }
    ),
    "call_restlet": MCPTool(
        name="call_restlet",
        description="Call a custom NetSuite RESTlet endpoint with specified method and data.",
        input_schema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full RESTlet URL (e.g., https://xxx.restlets.api.netsuite.com/...)"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE"],
                    "description": "HTTP method to use"
                },
                "body": {
                    "type": "object",
                    "description": "Request body data (for POST/PUT requests)"
                },
                "params": {
                    "type": "object",
                    "description": "URL query parameters"
                }
            },
            "required": ["url", "method"]
        }
    ),
    "list_records": MCPTool(
        name="list_records",
        description="List NetSuite records of a specific type with optional filtering.",
        input_schema={
            "type": "object",
            "properties": {
                "record_type": {
                    "type": "string",
                    "description": "NetSuite record type to list"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of records to return",
                    "default": 100
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of records to skip",
                    "default": 0
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to return"
                }
            },
            "required": ["record_type"]
        }
    ),
    "run_saved_search": MCPTool(
        name="run_saved_search",
        description="Execute a saved search by ID and return results.",
        input_schema={
            "type": "object",
            "properties": {
                "search_id": {
                    "type": "string",
                    "description": "Internal ID of the saved search"
                },
                "filters": {
                    "type": "object",
                    "description": "Additional filter criteria to apply"
                }
            },
            "required": ["search_id"]
        }
    )
}


class MCPToolHandler:
    """Handles execution of MCP tools using NetSuite connector."""
    
    def __init__(self, netsuite: NetSuite, odbc: ODBC):
        self.netsuite = netsuite
        self.odbc = odbc
        self._account_base_url = self._build_base_url()
    
    def _build_base_url(self) -> str:
        """Build the base REST API URL for the account."""
        account_id = str(self.netsuite.account_id).lower().replace("_", "-")
        return f"https://{account_id}.suitetalk.api.netsuite.com/services/rest/record/v1"
    
    def _format_response(self, result: NetsuiteObject) -> dict:
        """Format NetsuiteObject as MCP response content."""
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
    
    def _format_error(self, message: str) -> dict:
        """Format an error response."""
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": message}, indent=2)
            }],
            "isError": True
        }
    
    def handle_query_netsuite(self, params: dict) -> dict:
        """Execute SuiteQL query."""
        query = params.get("query")
        if not query:
            return self._format_error("Query parameter is required")
        
        result = self.odbc.query(query)
        return self._format_response(result)
    
    def handle_get_record(self, params: dict) -> dict:
        """Retrieve record by type and ID."""
        record_type = params.get("record_type")
        record_id = params.get("record_id")
        expand = params.get("expand_sub_resources", False)
        
        if not record_type or not record_id:
            return self._format_error("record_type and record_id are required")
        
        url = f"{self._account_base_url}/{record_type}/{record_id}"
        if expand:
            url += "?expandSubResources=true"
        
        result = self.netsuite.get(
            url=url,
            headers={"Content-Type": "application/json"}
        )
        return self._format_response(result)
    
    def handle_create_record(self, params: dict) -> dict:
        """Create a new record."""
        record_type = params.get("record_type")
        data = params.get("data")
        
        if not record_type or not data:
            return self._format_error("record_type and data are required")
        
        url = f"{self._account_base_url}/{record_type}"
        result = self.netsuite.post(
            url=url,
            headers={"Content-Type": "application/json"},
            body=data
        )
        return self._format_response(result)
    
    def handle_update_record(self, params: dict) -> dict:
        """Update an existing record."""
        record_type = params.get("record_type")
        record_id = params.get("record_id")
        data = params.get("data")
        
        if not record_type or not record_id or not data:
            return self._format_error("record_type, record_id, and data are required")
        
        url = f"{self._account_base_url}/{record_type}/{record_id}"
        result = self.netsuite.put(
            url=url,
            headers={"Content-Type": "application/json"},
            body=data
        )
        return self._format_response(result)
    
    def handle_delete_record(self, params: dict) -> dict:
        """Delete a record."""
        record_type = params.get("record_type")
        record_id = params.get("record_id")
        
        if not record_type or not record_id:
            return self._format_error("record_type and record_id are required")
        
        url = f"{self._account_base_url}/{record_type}/{record_id}"
        result = self.netsuite.delete(
            url=url,
            headers={"Content-Type": "application/json"}
        )
        return self._format_response(result)
    
    def handle_call_restlet(self, params: dict) -> dict:
        """Call custom RESTlet endpoint."""
        url = params.get("url")
        method = params.get("method", "GET").upper()
        body = params.get("body")
        query_params = params.get("params")
        
        if not url:
            return self._format_error("url is required")
        
        method_map = {
            "GET": self.netsuite.get,
            "POST": self.netsuite.post,
            "PUT": self.netsuite.put,
            "DELETE": self.netsuite.delete
        }
        
        handler = method_map.get(method)
        if not handler:
            return self._format_error(f"Unsupported HTTP method: {method}")
        
        kwargs: dict[str, Any] = {
            "url": url,
            "headers": {"Content-Type": "application/json"}
        }
        if query_params:
            kwargs["params"] = query_params
        if body and method in ("POST", "PUT"):
            kwargs["body"] = body
        
        result = handler(**kwargs)
        return self._format_response(result)
    
    def handle_list_records(self, params: dict) -> dict:
        """List records of a specific type."""
        record_type = params.get("record_type")
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        fields = params.get("fields", [])
        
        if not record_type:
            return self._format_error("record_type is required")
        
        url = f"{self._account_base_url}/{record_type}"
        query_params = {"limit": str(limit), "offset": str(offset)}
        if fields:
            query_params["fields"] = ",".join(fields)
        
        result = self.netsuite.get(
            url=url,
            headers={"Content-Type": "application/json"},
            params=query_params
        )
        return self._format_response(result)
    
    def handle_run_saved_search(self, params: dict) -> dict:
        """Execute a saved search."""
        search_id = params.get("search_id")
        filters = params.get("filters", {})
        
        if not search_id:
            return self._format_error("search_id is required")
        
        query = f"SELECT * FROM CUSTOMSEARCH{search_id}"
        if filters:
            filter_clauses = [f"{k} = '{v}'" for k, v in filters.items()]
            query += f" WHERE {' AND '.join(filter_clauses)}"
        
        result = self.odbc.query(query)
        return self._format_response(result)
    
    def call_tool(self, name: str, arguments: dict) -> dict:
        """Route tool call to appropriate handler."""
        handlers = {
            "query_netsuite": self.handle_query_netsuite,
            "get_record": self.handle_get_record,
            "create_record": self.handle_create_record,
            "update_record": self.handle_update_record,
            "delete_record": self.handle_delete_record,
            "call_restlet": self.handle_call_restlet,
            "list_records": self.handle_list_records,
            "run_saved_search": self.handle_run_saved_search,
        }
        
        handler = handlers.get(name)
        if not handler:
            return self._format_error(f"Unknown tool: {name}")
        
        try:
            return handler(arguments)
        except Exception as e:
            return self._format_error(f"Tool execution error: {str(e)}")


def get_tool_definitions() -> list[dict]:
    """Return all tool definitions in MCP format."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.input_schema
        }
        for tool in TOOL_SCHEMAS.values()
    ]
