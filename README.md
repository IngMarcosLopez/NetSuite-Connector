# NetSuite-Connector

## Supports

- [SuiteTalk REST Web Services](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/book_1559132836.html)
- [Restlets](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4387799403.html#Related-Support-Articles)

## Installation

    $ pip install NetSuite-Connector

## Get Started

The following examples shows how to use this module.

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
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx', request_headers={'Content-Type': 'application/json'}, response='{"foo":"bar"}', code=200)
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
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx', request_headers={'Content-Type': 'application/json'}, request_data={"foo":"bar"}, response='{"foo":"bar"}', code=200)
```

# SuiteQL Queries

To execute SuiteQL queries through REST web services, send a POST request to the `suiteql` resource, and specify the query in the request body after the query parameter `q`. The following example shows a SuiteQL query executed through REST web services.

### SuiteQL Query

```python
from NetSuite_Connector.ODBC import ODBC

nt = ODBC(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)
q = nt.query("SELECT top 10 * FROM transaction")
print(q)
# NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx', request_headers={'Content-Type': 'application/json'}, request_data={"foo":"bar"}, response='{"foo":"bar"}', code=200)
```
