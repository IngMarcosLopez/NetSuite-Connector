"""
Demo: How the NetSuite MCP Server works

This demonstrates the MCP server integration with the new modular structure.
"""
import json
import sys
sys.path.insert(0, "/home/runner/workspace/src")

print("=" * 60)
print("NetSuite MCP Server - Integration Demo")
print("=" * 60)

print("\n1. TESTING MCP CONFIG MODULE")
print("-" * 40)

from NetSuite_Connector.mcp_config import NetSuiteConfig, load_config_from_env, validate_config

config = NetSuiteConfig(
    account_id="123456_SB1",
    consumer_key="test_consumer_key",
    consumer_secret="test_consumer_secret",
    token_key="test_token_key",
    token_secret="test_token_secret"
)
print(f"Config created: account_id={config.account_id}")
print(f"Consumer keys: {list(config.consumer_keys.keys())}")
print(f"Token keys: {list(config.token_keys.keys())}")

errors = validate_config(config)
print(f"Validation errors: {errors if errors else 'None - config is valid'}")

print("\n2. TESTING MCP TOOLS MODULE")
print("-" * 40)

from NetSuite_Connector.mcp_tools import get_tool_definitions, TOOL_SCHEMAS

tools = get_tool_definitions()
print(f"Total tools available: {len(tools)}")
for tool in tools:
    required = tool.get('inputSchema', {}).get('required', [])
    print(f"  - {tool['name']}: {len(required)} required params")

print("\n3. TESTING MCP SERVER MODULE")
print("-" * 40)

from NetSuite_Connector.mcp_server import NetSuiteMCPServer

server = NetSuiteMCPServer(
    account_id="123456_SB1",
    consumer_keys={"consumer_key": "test", "consumer_secret": "test"},
    token_keys={"token_key": "test", "token_secret": "test"}
)

print(f"Server created: version {server.VERSION}")
print(f"Protocol version: {server.PROTOCOL_VERSION}")
print(f"Tools registered: {len(server.list_tools())}")

print("\n4. MCP PROTOCOL FLOW SIMULATION")
print("-" * 40)

init_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
init_response = server.handle_mcp_request(init_request)
print(f"[initialize] Server info: {init_response['result']['serverInfo']['name']}")

list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
list_response = server.handle_mcp_request(list_request)
print(f"[tools/list] Found {len(list_response['result']['tools'])} tools")

ping_request = {"jsonrpc": "2.0", "id": 3, "method": "ping"}
ping_response = server.handle_mcp_request(ping_request)
print(f"[ping] Response: {ping_response['result']}")

unknown_request = {"jsonrpc": "2.0", "id": 4, "method": "unknown/method"}
unknown_response = server.handle_mcp_request(unknown_request)
print(f"[unknown] Error handled: {unknown_response.get('error', {}).get('code')}")

print("\n5. CLAUDE DESKTOP CONFIGURATION")
print("-" * 40)

claude_config = {
    "mcpServers": {
        "netsuite": {
            "command": "python",
            "args": ["-m", "NetSuite_Connector"],
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

print("Config file locations:")
print("  Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
print("  macOS:   ~/Library/Application Support/Claude/claude_desktop_config.json")
print(f"\nSample config:\n{json.dumps(claude_config, indent=2)}")

print("\n6. TOOL DETAILS")
print("-" * 40)

for tool in server.list_tools():
    print(f"\n{tool['name']}:")
    print(f"  {tool['description'][:60]}...")
    props = tool.get('inputSchema', {}).get('properties', {})
    required = tool.get('inputSchema', {}).get('required', [])
    for prop_name in props:
        marker = "*" if prop_name in required else " "
        print(f"    {marker} {prop_name}")

print("\n" + "=" * 60)
print("Demo complete! All modules integrated successfully.")
print("=" * 60)
