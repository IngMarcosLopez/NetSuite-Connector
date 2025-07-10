
# NetSuite-Connector

A Python wrapper for NetSuite REST API that supports both OAuth 1.0 Token-Based Authentication (TBA) and OAuth 2.0 Machine-to-Machine (M2M) Authentication.

## Features

- [SuiteTalk REST Web Services](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/book_1559132836.html)
- [Restlets](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4387799403.html#Related-Support-Articles)
- OAuth 1.0 Token-Based Authentication (TBA)
- OAuth 2.0 Machine-to-Machine (M2M) Authentication
- SuiteQL Query Support

## Installation

```bash
pip install NetSuite-Connector
```

## OAuth 1.0 Authentication (TBA)

### NetSuite Class

The `NetSuite` class provides OAuth 1.0 authentication for REST API operations.

#### Constructor

```python
NetSuite(account_id, consumer_keys, token_keys)
```

**Parameters:**
- `account_id` (str/int): NetSuite account ID
- `consumer_keys` (dict): Dictionary with `consumer_key` and `consumer_secret`
- `token_keys` (dict): Dictionary with `token_key` and `token_secret`

#### Methods

##### get()

**Purpose:** Make a GET request to NetSuite REST API

**Parameters:**
- `url` (str): The REST API endpoint URL
- `headers` (dict, optional): HTTP headers
- `params` (dict, optional): Query parameters

**Returns:** `NetsuiteObject` with response data

**Example:**
```python
from NetSuite_Connector.NetSuite import NetSuite

nt = NetSuite(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)

response = nt.get(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    params={"foo": "bar"}
)
print(response)
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/...', request_headers={'Content-Type': 'application/json'}, response='{"foo":"bar"}', code=200)
```

##### post()

**Purpose:** Make a POST request to NetSuite REST API

**Parameters:**
- `url` (str): The REST API endpoint URL
- `headers` (dict, optional): HTTP headers
- `params` (dict, optional): Query parameters
- `body` (dict/str, optional): Request body data

**Returns:** `NetsuiteObject` with response data

**Example:**
```python
from NetSuite_Connector.NetSuite import NetSuite

nt = NetSuite(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)

body = {"foo": "bar"}
response = nt.post(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    body=body
)
print(response)
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/...', request_headers={'Content-Type': 'application/json'}, request_data={"foo":"bar"}, response='{"success":true}', code=200)
```

##### put()

**Purpose:** Make a PUT request to NetSuite REST API

**Parameters:**
- `url` (str): The REST API endpoint URL
- `headers` (dict, optional): HTTP headers
- `params` (dict, optional): Query parameters
- `body` (dict/str, optional): Request body data

**Returns:** `NetsuiteObject` with response data

**Example:**
```python
from NetSuite_Connector.NetSuite import NetSuite

nt = NetSuite(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)

body = {"id": 123, "status": "updated"}
response = nt.put(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    body=body
)
print(response)
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/...', response='{"updated":true}', code=200)
```

##### delete()

**Purpose:** Make a DELETE request to NetSuite REST API

**Parameters:**
- `url` (str): The REST API endpoint URL
- `headers` (dict, optional): HTTP headers
- `params` (dict, optional): Query parameters

**Returns:** `NetsuiteObject` with response data

**Example:**
```python
from NetSuite_Connector.NetSuite import NetSuite

nt = NetSuite(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)

response = nt.delete(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    params={"id": 123}
)
print(response)
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/...', response='{"deleted":true}', code=200)
```

### ODBC Class (OAuth 1.0 SuiteQL)

The `ODBC` class extends NetSuite for SuiteQL query operations using OAuth 1.0.

#### Constructor

```python
ODBC(account_id, consumer_keys, token_keys)
```

**Parameters:**
- `account_id` (str/int): NetSuite account ID
- `consumer_keys` (dict): Dictionary with `consumer_key` and `consumer_secret`
- `token_keys` (dict): Dictionary with `token_key` and `token_secret`

#### Methods

##### query()

**Purpose:** Execute SuiteQL queries using OAuth 1.0 authentication

**Parameters:**
- `query` (str): Fully qualified SQL query string

**Returns:** `NetsuiteObject` with query results

**Example:**
```python
from NetSuite_Connector.ODBC import ODBC

nt = ODBC(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)

result = nt.query("SELECT TOP 10 * FROM transaction")
print(result)
# NetsuiteObject(url='https://xxxx.suitetalk.api.netsuite.com/...', response='{"items":[...]}', code=200)
```

## OAuth 2.0 Authentication (M2M)

### NetSuiteOAuth2Client Class

The `NetSuiteOAuth2Client` class provides OAuth 2.0 Machine-to-Machine authentication for REST API operations.

#### Constructor

```python
NetSuiteOAuth2Client(account_id, client_id, certificate_id, private_key, scope)
```

**Parameters:**
- `account_id` (str): NetSuite account ID
- `client_id` (str): OAuth 2.0 client ID
- `certificate_id` (str): Certificate ID for JWT signing
- `private_key` (str): PEM format private key
- `scope` (str, optional): OAuth scope, defaults to "restlets,rest_webservices"

#### Methods

##### get()

**Purpose:** Make a GET request using OAuth 2.0 authentication

**Parameters:**
- `url` (str): The REST API endpoint URL
- `headers` (dict, optional): HTTP headers
- `params` (dict, optional): Query parameters

**Returns:** `NetsuiteObject` with response data

**Example:**
```python
from NetSuite_Connector.NetSuiteOAuth2Client import NetSuiteOAuth2Client

client = NetSuiteOAuth2Client(
    account_id="123456",
    client_id="your_client_id",
    certificate_id="your_certificate_id",
    private_key="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----"
)

response = client.get(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"}
)
print(response)
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/...', response='{"data":"success"}', code=200)
```

##### post()

**Purpose:** Make a POST request using OAuth 2.0 authentication

**Parameters:**
- `url` (str): The REST API endpoint URL
- `headers` (dict, optional): HTTP headers
- `params` (dict, optional): Query parameters
- `body` (dict/str, optional): Request body data

**Returns:** `NetsuiteObject` with response data

**Example:**
```python
from NetSuite_Connector.NetSuiteOAuth2Client import NetSuiteOAuth2Client

client = NetSuiteOAuth2Client(
    account_id="123456",
    client_id="your_client_id",
    certificate_id="your_certificate_id",
    private_key="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----"
)

body = {"foo": "bar"}
response = client.post(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    body=body
)
print(response)
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/...', request_data={"foo":"bar"}, response='{"success":true}', code=200)
```

##### put()

**Purpose:** Make a PUT request using OAuth 2.0 authentication

**Parameters:**
- `url` (str): The REST API endpoint URL
- `headers` (dict, optional): HTTP headers
- `params` (dict, optional): Query parameters
- `body` (dict/str, optional): Request body data

**Returns:** `NetsuiteObject` with response data

**Example:**
```python
from NetSuite_Connector.NetSuiteOAuth2Client import NetSuiteOAuth2Client

client = NetSuiteOAuth2Client(
    account_id="123456",
    client_id="your_client_id",
    certificate_id="your_certificate_id",
    private_key="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----"
)

body = {"id": 123, "status": "updated"}
response = client.put(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    body=body
)
print(response)
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/...', response='{"updated":true}', code=200)
```

##### delete()

**Purpose:** Make a DELETE request using OAuth 2.0 authentication

**Parameters:**
- `url` (str): The REST API endpoint URL
- `headers` (dict, optional): HTTP headers
- `params` (dict, optional): Query parameters

**Returns:** `NetsuiteObject` with response data

**Example:**
```python
from NetSuite_Connector.NetSuiteOAuth2Client import NetSuiteOAuth2Client

client = NetSuiteOAuth2Client(
    account_id="123456",
    client_id="your_client_id",
    certificate_id="your_certificate_id",
    private_key="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----"
)

response = client.delete(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    params={"id": 123}
)
print(response)
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/...', response='{"deleted":true}', code=200)
```

### OAuth2ODBC Class (OAuth 2.0 SuiteQL)

The `OAuth2ODBC` class extends NetSuiteOAuth2Client for SuiteQL query operations using OAuth 2.0.

#### Constructor

```python
OAuth2ODBC(account_id, client_id, certificate_id, private_key, scope)
```

**Parameters:**
- `account_id` (str): NetSuite account ID
- `client_id` (str): OAuth 2.0 client ID
- `certificate_id` (str): Certificate ID for JWT signing
- `private_key` (str): PEM format private key
- `scope` (str, optional): OAuth scope, defaults to "restlets,rest_webservices"

#### Methods

##### query()

**Purpose:** Execute SuiteQL queries using OAuth 2.0 authentication

**Parameters:**
- `query` (str): Fully qualified SQL query string

**Returns:** `NetsuiteObject` with query results

**Example:**
```python
from NetSuite_Connector.OAuth2ODBC import OAuth2ODBC

odbc = OAuth2ODBC(
    account_id="123456",
    client_id="your_client_id",
    certificate_id="your_certificate_id",
    private_key="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----"
)

result = odbc.query("SELECT TOP 10 * FROM transaction")
print(result)
# NetsuiteObject(url='https://xxxx.suitetalk.api.netsuite.com/...', response='{"items":[...]}', code=200)
```

## NetsuiteObject Response Format

All methods return a `NetsuiteObject` with the following attributes:

- `url` (str): The request URL
- `request_headers` (dict): Headers sent with the request
- `request_data` (dict/str): Data sent with the request
- `response` (str): Response body from NetSuite
- `code` (int): HTTP status code
- `json` (property): Returns the object as a dictionary

## Error Handling

All methods handle exceptions gracefully and return error information in the `NetsuiteObject`:

- `code`: 500 for internal errors, 401 for authentication failures
- `response`: Error message or exception details

## Requirements

- Python 3.11+
- requests>=2.32.4
- requests-oauthlib>=2.0.0
- cryptography>=45.0.5
- pandas>=2.3.1
- numpy>=2.3.1
- oauthlib>=3.3.1
- setuptools>=80.9.0

### Development/Testing Dependencies

- pytest>=8.4.1
- pytest-mock>=3.14.0
- requests-mock>=1.12.1

## License

MIT License
