from .NetSuite import NetsuiteObject
from .NetSuiteOAuth2Client import NetSuiteOAuth2Client


class OAuth2ODBC(NetSuiteOAuth2Client):
    """
    OAuth 2.0 version of the ODBC class for executing SuiteQL queries.

    Usage:
    ```python
    from NetSuite_Connector.OAuth2ODBC import OAuth2ODBC

    odbc = OAuth2ODBC(
        account_id="123456",
        client_id="your_client_id",
        certificate_id="your_certificate_id",
        private_key="-----BEGIN PRIVATE KEY-----\n....\n-----END PRIVATE KEY-----"
    )

    result = odbc.query("SELECT TOP 10 * FROM transaction")
    ```
    """

    def __init__(
        self,
        account_id: str,
        client_id: str,
        certificate_id: str,
        private_key: str,
        scope: str = "restlets,rest_webservices",
    ):
        super().__init__(account_id, client_id, certificate_id, private_key, scope)
        # Use the formatted account ID from the OAuth2Config
        self.suiteql_endpoint = f'https://{self.oauth2_client.config.formatted_account_id}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql'

    def query(self, query: str) -> NetsuiteObject:
        """
        Execute a SuiteQL query using OAuth 2.0 authentication.

        Args:
            query: Fully qualified SQL query

        Returns:
            NetsuiteObject: Response containing query results
        """
        response = NetsuiteObject(request_data=query)

        try:
            data = {"q": query}
            headers = {
                "prefer": "transient",
                "Content-Type": "application/json",
            }  # ignore: E501

            req = self.post(
                url=self.suiteql_endpoint, body=data, headers=headers
            )  # ignore: E501

            response.url = self.suiteql_endpoint
            response.request_headers = headers
            response.response = req.response
            response.code = req.code

        except Exception as e:
            response.response = f"Error executing query: {str(e)}"
            response.code = 500

        return response
