# NetSuite-Connector

A Python library for connecting to NetSuite via REST API, SuiteQL, and MCP (Model Context Protocol) for AI integration.

## Supports

- [SuiteTalk REST Web Services](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/book_1559132836.html)
- [Restlets](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4387799403.html#Related-Support-Articles)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) for AI Integration

## Installation

```bash
pip install NetSuite-Connector
```

## Get Started

The following examples show how to use this module.

### RESTlet GET

```python
from NetSuite_Connector.NetSuite import NetSuite
nt = NetSuite(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)

x = nt.get(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    params={"foo":"bar"}
)
print(x)
# NetsuiteObject(url='...', request_headers={...}, response='{"foo":"bar"}', code=200)
```

### RESTlet PUT - POST - DELETE

```python
from NetSuite_Connector.NetSuite import NetSuite
nt = NetSuite(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)
body={"foo":"bar"}
x = nt.post(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    params={},
    body=body
)
print(x)
```

## SuiteQL Queries

Execute SuiteQL queries through REST web services.

```python
from NetSuite_Connector.ODBC import ODBC

nt = ODBC(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)
q = nt.query("SELECT top 10 * FROM transaction")
print(q)
```

---

## MCP Server Integration (AI Assistants)

The library includes an MCP (Model Context Protocol) server that allows AI assistants like Claude, ChatGPT, and custom agents to interact with NetSuite data using natural language.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `query_netsuite` | Execute SuiteQL queries |
| `get_record` | Retrieve record by type and ID |
| `create_record` | Create new NetSuite records |
| `update_record` | Update existing records |
| `delete_record` | Delete records |
| `call_restlet` | Call custom RESTlet endpoints |
| `list_records` | List records with pagination |
| `run_saved_search` | Execute saved searches |

### Option 1: Programmatic Usage

```python
from NetSuite_Connector.mcp_server import NetSuiteMCPServer

# Initialize the MCP server
server = NetSuiteMCPServer(
    account_id="123456_SB1",
    consumer_keys={"consumer_key": "xxx", "consumer_secret": "yyy"},
    token_keys={"token_key": "aaa", "token_secret": "bbb"}
)

# List available tools
tools = server.list_tools()
print(f"Available tools: {[t['name'] for t in tools]}")

# Call a tool
result = server.call_tool("query_netsuite", {
    "query": "SELECT TOP 10 id, companyname FROM customer"
})
print(result)
```

### Option 2: Claude Desktop Integration

Add to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "netsuite": {
      "command": "python",
      "args": ["-m", "NetSuite_Connector"],
      "env": {
        "NETSUITE_ACCOUNT_ID": "YOUR_ACCOUNT_ID",
        "NETSUITE_CONSUMER_KEY": "YOUR_CONSUMER_KEY",
        "NETSUITE_CONSUMER_SECRET": "YOUR_CONSUMER_SECRET",
        "NETSUITE_TOKEN_KEY": "YOUR_TOKEN_KEY",
        "NETSUITE_TOKEN_SECRET": "YOUR_TOKEN_SECRET"
      }
    }
  }
}
```

Then in Claude, you can ask questions like:
- "Show me the top 10 customers"
- "Get invoice #12345"
- "What's the total revenue this quarter?"

### Option 3: CLI Usage

```bash
# Check configuration
python -m NetSuite_Connector --check-config

# List available tools
python -m NetSuite_Connector --list-tools

# Run as stdio server (for MCP clients)
python -m NetSuite_Connector
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `NETSUITE_ACCOUNT_ID` | NetSuite account ID (e.g., 123456_SB1) |
| `NETSUITE_CONSUMER_KEY` | OAuth consumer key |
| `NETSUITE_CONSUMER_SECRET` | OAuth consumer secret |
| `NETSUITE_TOKEN_KEY` | Token-based auth token key |
| `NETSUITE_TOKEN_SECRET` | Token-based auth token secret |

---

## Authentication

This library uses **Token-Based Authentication (TBA)** with OAuth 1.0 and HMAC-SHA256 signatures.

### Setting up TBA in NetSuite

1. Enable Token-Based Authentication in your NetSuite account
2. Create an Integration record to get Consumer Key and Secret
3. Create an Access Token for your user to get Token Key and Secret
4. Use these credentials with the library

---

## Development

### Install dev dependencies

```bash
pip install NetSuite-Connector[dev]
```

### Run tests

```bash
pytest tests/ -v --cov=src/NetSuite_Connector
```

---

## License

MIT License
