"""
Demo: How the NetSuite MCP Server works

This demonstrates the MCP server without requiring actual NetSuite credentials.
It shows the tool registration, listing, and calling patterns.
"""
import json
import os

print("=" * 60)
print("NetSuite MCP Server - Demo")
print("=" * 60)

print("\n1. MCP TOOL DEFINITIONS")
print("-" * 40)

tools = [
    {
        "name": "query_netsuite",
        "description": "Execute a SuiteQL query against NetSuite",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SuiteQL query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "call_restlet",
        "description": "Call a NetSuite RESTlet endpoint",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                "body": {"type": "object"}
            },
            "required": ["url", "method"]
        }
    },
    {
        "name": "get_record",
        "description": "Retrieve a NetSuite record by type and ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "record_type": {"type": "string"},
                "record_id": {"type": "string"}
            },
            "required": ["record_type", "record_id"]
        }
    }
]

for tool in tools:
    print(f"\nTool: {tool['name']}")
    print(f"  Description: {tool['description']}")
    print(f"  Required params: {tool['inputSchema'].get('required', [])}")

print("\n\n2. MCP PROTOCOL FLOW")
print("-" * 40)

print("\n[Step 1] AI Client sends 'initialize' request:")
init_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
print(f"  Request:  {json.dumps(init_request)}")

init_response = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "netsuite-connector-mcp", "version": "0.1.0"}
    }
}
print(f"  Response: {json.dumps(init_response, indent=2)}")

print("\n[Step 2] AI Client requests 'tools/list':")
list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
print(f"  Request:  {json.dumps(list_request)}")
print(f"  Response: <returns {len(tools)} tool definitions>")

print("\n[Step 3] AI Client calls a tool 'tools/call':")
call_request = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "query_netsuite",
        "arguments": {"query": "SELECT TOP 5 id, companyname FROM customer"}
    }
}
print(f"  Request:  {json.dumps(call_request, indent=2)}")

mock_response = {
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "status_code": 200,
                "data": {
                    "items": [
                        {"id": "101", "companyname": "Acme Corp"},
                        {"id": "102", "companyname": "TechStart Inc"}
                    ]
                }
            })
        }]
    }
}
print(f"  Response: {json.dumps(mock_response, indent=2)}")

print("\n\n3. CLAUDE DESKTOP CONFIGURATION")
print("-" * 40)

claude_config = {
    "mcpServers": {
        "netsuite": {
            "command": "python",
            "args": ["-m", "NetSuite_Connector.mcp_server"],
            "env": {
                "NETSUITE_ACCOUNT_ID": "your_account_id",
                "NETSUITE_CONSUMER_KEY": "your_consumer_key",
                "NETSUITE_CONSUMER_SECRET": "your_consumer_secret",
                "NETSUITE_TOKEN_KEY": "your_token_key",
                "NETSUITE_TOKEN_SECRET": "your_token_secret"
            }
        }
    }
}

print("\nAdd this to your Claude Desktop config file:")
print("  Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
print("  macOS:   ~/Library/Application Support/Claude/claude_desktop_config.json")
print(f"\n{json.dumps(claude_config, indent=2)}")

print("\n\n4. USAGE EXAMPLE (with real credentials)")
print("-" * 40)
print("""
from NetSuite_Connector.mcp_server import NetSuiteMCPServer

# Initialize the server
server = NetSuiteMCPServer(
    account_id="123456_SB1",
    consumer_keys={"consumer_key": "xxx", "consumer_secret": "yyy"},
    token_keys={"token_key": "aaa", "token_secret": "bbb"}
)

# List available tools
tools = server.list_tools()
print(f"Available tools: {[t['name'] for t in tools]}")

# Call a tool (AI would do this)
result = server.call_tool("query_netsuite", {
    "query": "SELECT TOP 10 * FROM customer"
})
print(result)
""")

print("\n" + "=" * 60)
print("Demo complete! The MCP server is ready for integration.")
print("=" * 60)
