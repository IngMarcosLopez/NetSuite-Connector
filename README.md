<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/NetSuite-ERP-orange?style=for-the-badge" alt="NetSuite">
  <img src="https://img.shields.io/badge/MCP-AI%20Ready-purple?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/Coverage-98%25-brightgreen?style=for-the-badge" alt="Coverage">
</p>

<h1 align="center">NetSuite-Connector</h1>

<p align="center">
  <strong>The simplest way to connect Python to NetSuite</strong><br>
  REST API • SuiteQL Queries • AI Assistant Integration
</p>

<p align="center">
  <a href="#-installation">Installation</a> · 
  <a href="#-quick-start">Quick Start</a> · 
  <a href="#-suiteql-queries">SuiteQL</a> · 
  <a href="#-ai-integration">AI Integration</a> · 
  <a href="#-reference">Reference</a>
</p>

---

<br>

## Installation

```bash
pip install NetSuite-Connector
```

<br>

---

<br>

## Quick Start

### 1. Gather Your Credentials

You need 5 values from NetSuite:

<table>
<tr>
<td width="200"><strong>Credential</strong></td>
<td><strong>Where to Find</strong></td>
</tr>
<tr>
<td>Account ID</td>
<td><code>Setup</code> → <code>Company</code> → <code>Company Information</code></td>
</tr>
<tr>
<td>Consumer Key</td>
<td><code>Setup</code> → <code>Integration</code> → <code>Manage Integrations</code></td>
</tr>
<tr>
<td>Consumer Secret</td>
<td>Generated when you create the integration</td>
</tr>
<tr>
<td>Token Key</td>
<td><code>Setup</code> → <code>Users/Roles</code> → <code>Access Tokens</code></td>
</tr>
<tr>
<td>Token Secret</td>
<td>Generated when you create the access token</td>
</tr>
</table>

<br>

### 2. Connect and Make Your First Request

```python
from NetSuite_Connector.NetSuite import NetSuite

# Create your connection
client = NetSuite(
    account_id="123456_SB1",
    consumer_keys={
        "consumer_key": "your_consumer_key",
        "consumer_secret": "your_consumer_secret"
    },
    token_keys={
        "token_key": "your_token_key",
        "token_secret": "your_token_secret"
    }
)

# Fetch a customer record
response = client.get(
    url="https://123456.suitetalk.api.netsuite.com/services/rest/record/v1/customer/123"
)

print(response.code)      # 200
print(response.response)  # {"id": "123", "companyName": "Acme Corp", ...}
```

<br>

---

<br>

## Working with Records

<table>
<tr>
<td width="120" align="center"><h3>GET</h3></td>
<td>

```python
# Retrieve a record
result = client.get(url=".../customer/123")
```

</td>
</tr>
<tr>
<td align="center"><h3>POST</h3></td>
<td>

```python
# Create a new record
result = client.post(
    url=".../customer",
    body={"companyName": "New Company", "email": "hello@company.com"}
)
```

</td>
</tr>
<tr>
<td align="center"><h3>PUT</h3></td>
<td>

```python
# Update an existing record
result = client.put(
    url=".../customer/123",
    body={"email": "updated@company.com"}
)
```

</td>
</tr>
<tr>
<td align="center"><h3>DELETE</h3></td>
<td>

```python
# Delete a record
result = client.delete(url=".../customer/123")
```

</td>
</tr>
</table>

<br>

---

<br>

## SuiteQL Queries

Run SQL-like queries directly against your NetSuite data.

```python
from NetSuite_Connector.ODBC import ODBC

db = ODBC(
    account_id="123456_SB1",
    consumer_keys={"consumer_key": "...", "consumer_secret": "..."},
    token_keys={"token_key": "...", "token_secret": "..."}
)

# Get active customers
result = db.query("""
    SELECT id, companyname, email 
    FROM customer 
    WHERE isinactive = 'F'
    ORDER BY companyname
""")
```

<br>

### Example Queries

<table>
<tr><td width="250"><strong>Get all active customers</strong></td>
<td><code>SELECT * FROM customer WHERE isinactive = 'F'</code></td></tr>

<tr><td><strong>Recent invoices</strong></td>
<td><code>SELECT * FROM invoice WHERE trandate >= '2024-01-01'</code></td></tr>

<tr><td><strong>Open sales orders</strong></td>
<td><code>SELECT * FROM salesorder WHERE status = 'Pending Fulfillment'</code></td></tr>

<tr><td><strong>Product catalog</strong></td>
<td><code>SELECT itemid, displayname, baseprice FROM item</code></td></tr>

<tr><td><strong>Revenue by month</strong></td>
<td><code>SELECT EXTRACT(MONTH FROM trandate) as month, SUM(total) FROM invoice GROUP BY 1</code></td></tr>
</table>

<br>

---

<br>

## AI Integration

<p align="center">
  <strong>Let AI assistants work with your NetSuite data using natural language</strong>
</p>

<br>

### Available Tools

<table>
<tr>
<td width="180"><code>query_netsuite</code></td>
<td>Run SuiteQL queries</td>
</tr>
<tr>
<td><code>get_record</code></td>
<td>Fetch a specific record by ID</td>
</tr>
<tr>
<td><code>create_record</code></td>
<td>Create new records</td>
</tr>
<tr>
<td><code>update_record</code></td>
<td>Modify existing records</td>
</tr>
<tr>
<td><code>delete_record</code></td>
<td>Remove records</td>
</tr>
<tr>
<td><code>list_records</code></td>
<td>Browse records with pagination</td>
</tr>
<tr>
<td><code>call_restlet</code></td>
<td>Execute custom SuiteScripts</td>
</tr>
<tr>
<td><code>run_saved_search</code></td>
<td>Run saved searches</td>
</tr>
</table>

<br>

### Setup for Claude Desktop

<details>
<summary><strong>Click to expand setup instructions</strong></summary>

<br>

**Step 1:** Find your Claude config file

| System | Path |
|--------|------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

**Step 2:** Add this configuration

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

**Step 3:** Restart Claude Desktop

**Step 4:** Start asking questions!

> "Show me this month's top 10 customers by revenue"

> "Get the details for invoice #12345"

> "What sales orders are pending fulfillment?"

> "Create a new customer for Acme Corporation"

</details>

<br>

### Use in Python

```python
from NetSuite_Connector.mcp_server import NetSuiteMCPServer

server = NetSuiteMCPServer(
    account_id="123456_SB1",
    consumer_keys={"consumer_key": "...", "consumer_secret": "..."},
    token_keys={"token_key": "...", "token_secret": "..."}
)

# Run a query through the AI interface
result = server.call_tool("query_netsuite", {
    "query": "SELECT TOP 5 id, companyname FROM customer"
})
```

<br>

### Command Line

```bash
# Verify your credentials
python -m NetSuite_Connector --check-config

# List available tools
python -m NetSuite_Connector --list-tools

# Start the MCP server
python -m NetSuite_Connector
```

<br>

---

<br>

## Reference

### Response Object

Every request returns a `NetsuiteObject`:

```python
result = client.get(url="...")

result.code              # HTTP status code (200, 404, etc.)
result.response          # JSON response body
result.url               # URL that was called
result.request_headers   # Headers sent with request
```

<br>

### Status Codes

| Code | Status | Meaning |
|:----:|--------|---------|
| `200` | OK | Request successful |
| `201` | Created | Record created |
| `204` | No Content | Record deleted |
| `400` | Bad Request | Check your request data |
| `401` | Unauthorized | Check your credentials |
| `404` | Not Found | Record doesn't exist |
| `429` | Too Many Requests | Rate limited, wait and retry |

<br>

### Environment Variables

```bash
export NETSUITE_ACCOUNT_ID="123456_SB1"
export NETSUITE_CONSUMER_KEY="your_consumer_key"
export NETSUITE_CONSUMER_SECRET="your_consumer_secret"
export NETSUITE_TOKEN_KEY="your_token_key"
export NETSUITE_TOKEN_SECRET="your_token_secret"
```

<br>

---

<br>

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Authentication failed | Verify all 5 credentials are correct |
| Record not found | Check the record ID and your permissions |
| Rate limited | Wait 60 seconds before retrying |
| Connection timeout | Check your network connection |
| Invalid account ID | Format should be like `123456` or `123456_SB1` |

<br>

---

<br>

## Development

```bash
# Install with dev dependencies
pip install NetSuite-Connector[dev]

# Run tests
pytest tests/ -v --cov=src/NetSuite_Connector
```

<p align="center">
  <strong>121 tests</strong> · <strong>98% coverage</strong>
</p>

<br>

---

<p align="center">
  <strong>MIT License</strong> · Made with Python
</p>
