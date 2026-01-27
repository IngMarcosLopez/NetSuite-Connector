# NetSuite-Connector

<p align="center">
  <strong>Connect to NetSuite from Python with ease</strong>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-ai-integration">AI Integration</a> •
  <a href="#-api-reference">API Reference</a>
</p>

---

## What is NetSuite-Connector?

NetSuite-Connector is a Python library that lets you connect to NetSuite ERP in three ways:

| Method | Best For |
|--------|----------|
| **REST API** | Creating, reading, updating, and deleting records |
| **SuiteQL** | Running SQL-like queries on your NetSuite data |
| **MCP Server** | Letting AI assistants (like Claude) work with your NetSuite data |

---

## Quick Start

### Step 1: Install

```bash
pip install NetSuite-Connector
```

### Step 2: Get Your Credentials

You'll need these 5 values from your NetSuite account:

| Credential | Where to Find It |
|------------|------------------|
| Account ID | Setup > Company > Company Information |
| Consumer Key | Setup > Integration > Manage Integrations |
| Consumer Secret | (Generated when creating integration) |
| Token Key | Setup > Users/Roles > Access Tokens |
| Token Secret | (Generated when creating token) |

### Step 3: Start Using It

```python
from NetSuite_Connector.NetSuite import NetSuite

# Connect to NetSuite
client = NetSuite(
    account_id="123456_SB1",
    consumer_keys={"consumer_key": "your_key", "consumer_secret": "your_secret"},
    token_keys={"token_key": "your_token", "token_secret": "your_token_secret"}
)

# Get a customer record
result = client.get(url="https://123456.suitetalk.api.netsuite.com/services/rest/record/v1/customer/123")
print(result.response)
```

---

## Features

### REST API - Work with Records

**Get a record:**
```python
result = client.get(
    url="https://123456.suitetalk.api.netsuite.com/services/rest/record/v1/customer/123"
)
```

**Create a record:**
```python
result = client.post(
    url="https://123456.suitetalk.api.netsuite.com/services/rest/record/v1/customer",
    body={"companyName": "Acme Corp", "email": "contact@acme.com"}
)
```

**Update a record:**
```python
result = client.put(
    url="https://123456.suitetalk.api.netsuite.com/services/rest/record/v1/customer/123",
    body={"email": "newemail@acme.com"}
)
```

**Delete a record:**
```python
result = client.delete(
    url="https://123456.suitetalk.api.netsuite.com/services/rest/record/v1/customer/123"
)
```

---

### SuiteQL - Query Your Data

Run SQL-like queries to pull data from NetSuite:

```python
from NetSuite_Connector.ODBC import ODBC

# Connect
db = ODBC(
    account_id="123456_SB1",
    consumer_keys={"consumer_key": "your_key", "consumer_secret": "your_secret"},
    token_keys={"token_key": "your_token", "token_secret": "your_token_secret"}
)

# Run a query
result = db.query("SELECT id, companyname, email FROM customer WHERE isinactive = 'F'")
print(result.response)
```

**Common queries:**

| What You Want | Query |
|---------------|-------|
| Active customers | `SELECT * FROM customer WHERE isinactive = 'F'` |
| Recent invoices | `SELECT * FROM invoice WHERE trandate >= '2024-01-01'` |
| Open sales orders | `SELECT * FROM salesorder WHERE status = 'open'` |
| Item list | `SELECT id, itemid, displayname FROM item` |

---

## AI Integration

Let AI assistants like Claude interact with your NetSuite data using natural language.

### What Can the AI Do?

| Tool | What It Does |
|------|--------------|
| `query_netsuite` | Run SuiteQL queries |
| `get_record` | Fetch a specific record |
| `create_record` | Create new records |
| `update_record` | Update existing records |
| `delete_record` | Remove records |
| `call_restlet` | Call custom scripts |
| `list_records` | Browse records with filters |
| `run_saved_search` | Execute saved searches |

### Option A: Use with Claude Desktop

**1. Find your config file:**

| System | Location |
|--------|----------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

**2. Add this configuration:**

```json
{
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
```

**3. Restart Claude Desktop**

**4. Ask Claude things like:**
- "Show me the top 10 customers by revenue"
- "Get invoice number 12345"
- "What sales orders are pending this week?"
- "Create a new customer record for Acme Corp"

### Option B: Use in Your Python Code

```python
from NetSuite_Connector.mcp_server import NetSuiteMCPServer

# Create server
server = NetSuiteMCPServer(
    account_id="123456_SB1",
    consumer_keys={"consumer_key": "xxx", "consumer_secret": "yyy"},
    token_keys={"token_key": "aaa", "token_secret": "bbb"}
)

# List available tools
tools = server.list_tools()
print(f"Available: {[t['name'] for t in tools]}")

# Run a query
result = server.call_tool("query_netsuite", {
    "query": "SELECT TOP 5 id, companyname FROM customer"
})
print(result)
```

### Option C: Command Line

```bash
# Check if your credentials are set up correctly
python -m NetSuite_Connector --check-config

# See all available tools
python -m NetSuite_Connector --list-tools

# Start the server (for MCP clients)
python -m NetSuite_Connector
```

---

## API Reference

### Response Object

All methods return a `NetsuiteObject` with these properties:

| Property | Description |
|----------|-------------|
| `response` | The JSON response from NetSuite |
| `code` | HTTP status code (200 = success) |
| `url` | The URL that was called |
| `request_headers` | Headers that were sent |

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | Deleted |
| 400 | Bad request (check your data) |
| 401 | Authentication failed |
| 404 | Record not found |
| 500 | Server error |

---

## Environment Variables

Set these in your system or `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `NETSUITE_ACCOUNT_ID` | Yes | Your NetSuite account ID |
| `NETSUITE_CONSUMER_KEY` | Yes | OAuth consumer key |
| `NETSUITE_CONSUMER_SECRET` | Yes | OAuth consumer secret |
| `NETSUITE_TOKEN_KEY` | Yes | Access token key |
| `NETSUITE_TOKEN_SECRET` | Yes | Access token secret |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Invalid credentials" | Double-check all 5 credential values |
| "Record not found" | Verify the record ID exists and you have permission |
| "Rate limited" | Wait a moment and try again |
| "Connection timeout" | Check your internet connection |

---

## Development

### Run Tests

```bash
pip install NetSuite-Connector[dev]
pytest tests/ -v --cov=src/NetSuite_Connector
```

**Current coverage: 98% (121 tests)**

---

## License

MIT License - Use it however you like!
