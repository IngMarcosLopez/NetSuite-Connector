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
print(x.__dict__)
# Response <200>
```
### RESTlet PUT - POST
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
print(x.__dict__)
# Response <200>
```
## TODO
- DELETE Method
- JDBC Connection Support