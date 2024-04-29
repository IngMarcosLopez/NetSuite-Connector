import traceback
from typing import Any

from .NetSuite import NetSuite, NetsuiteObject


class ODBC(NetSuite):

    def __init__(self, account_id: Any, consumer_keys: dict, token_keys: dict) -> None:
        super().__init__(account_id, consumer_keys, token_keys)
        self.suiteql_endpoint = f'https://{account_id.lower().replace("_", "-")}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql'

    def query(self, query: str) -> NetsuiteObject:
        """
        Perfom a query to ODBC driver
        query: fully qualified sql query
        >>> from NetSuite_Connector.ODBC import ODBC

        >>> nt = ODBC(
            account_id=123456,
            consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
            token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije")
            )

        >>> q = nt.query("SELECT top 10 * FROM transaction")

        >>> NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx', request_headers={'Content-Type': 'application/json'}, response='{"foo":"bar"}', code=200)
        """
        response = NetsuiteObject(request_data=query)
        try:
            data = {"q": query}
            headers = {"prefer": "transient", "Content-Type": "application/json"}
            req = self.post(url=self.suiteql_endpoint, body=data, headers=headers)
            response.response = req.response
            response.code = req.code
        except Exception:
            response.code = 500
            response.response = traceback.format_exc()

        return response
