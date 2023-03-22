# NetSuite-Connector

## Installation

Only Restlet support:

    $ pip install NetSuite-Connector
## Get Started
The following examples shows how to use this module.

### RESTlet GET
```python
from NetSuite_Connector.NetSuite import NetSuite
nt = NetSuite(
    account_id=123456,
    consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
    token_keys=dict(token_id="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
)

x = nt.get(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    headers={"Content-Type": "application/json"},
    params={}
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
    token_keys=dict(token_id="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
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
# ODBC Queries

Connector only supports ODBC Driver queries, JDBC is not supported
## Get Started

Before you begin install [ODBC Driver](https://system.netsuite.com/app/help/helpcenter.nl?fid=book_N748613.html).

Note that Support for NetSuite2.com is supported, which means that Only roles that hat not activated 2FA are supported. Also note that role must have permission to SuiteAnalitics.

### ODBC Query

```python
from NetSuite_Connector.ODBC import ODBC

nt = ODBC(
    account_id="*****",
    user_email="*****",
    role_id="*****",
    dsn="*****",
    password="*****"
)
q = nt.query("SELECT * FROM OA_tables")
print(q.status)
# 200
print(q.response)
#[{"foo":"bar"}]
print(q.data_received)
# SELECT * FROM OA_tables
print(q.columns)
# ["foo"]
```


## TODO

- Add TBA for ODBC connector support