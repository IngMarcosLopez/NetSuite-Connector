# NetSuite-Connector

nt = Netsuite()

x = nt.get(
    url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
    body=[],
    headers={"Content-Type": "application/json"},
)
print(x.__dict__)