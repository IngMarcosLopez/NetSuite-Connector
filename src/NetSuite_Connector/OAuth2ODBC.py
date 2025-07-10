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

    def query(self, query: str, limit: int = None, offset: int = None) -> NetsuiteObject:
        """
        Perform a SuiteQL query using OAuth 2.0 authentication.

        According to NetSuite documentation, SuiteQL supports:
        - Standard SQL SELECT statements with NetSuite-specific syntax
        - LIMIT and OFFSET for pagination
        - Various built-in functions and operators

        Args:
            query: SuiteQL query string (e.g., "SELECT id, companyname FROM customer")
            limit: Optional limit for result set pagination
            offset: Optional offset for result set pagination

        Returns:
            NetsuiteObject: Response object containing query results

        Example:
            >>> client = OAuth2ODBC(
            ...     account_id="TSTDRV123456",
            ...     client_id="your_client_id", 
            ...     certificate_id="your_certificate_id",
            ...     private_key="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
            ... )
            >>> result = client.query("SELECT id, companyname FROM customer", limit=10)
            >>> result = client.query("SELECT * FROM transaction WHERE trandate >= '2024-01-01'")
        """
        response = NetsuiteObject(request_data=query, url=self.suiteql_endpoint)

        try:
            # Apply pagination if specified
            final_query = query
            if limit is not None:
                if "LIMIT" not in query.upper():
                    final_query += f" LIMIT {limit}"
            if offset is not None:
                if "OFFSET" not in query.upper():
                    final_query += f" OFFSET {offset}"

            data = {"q": final_query}

            # Headers as per NetSuite SuiteQL documentation
            headers = {
                "Content-Type": "application/json",
                "Prefer": "transient"  # For non-persistent queries
            }

            result = self.post(url=self.suiteql_endpoint, body=data, headers=headers)
            response.response = result.response
            response.code = result.code
            response.request_headers = headers
            response.request_data = data

        except Exception as e:
            response.code = 500
            response.response = f"SuiteQL query execution failed: {str(e)}"

        return response