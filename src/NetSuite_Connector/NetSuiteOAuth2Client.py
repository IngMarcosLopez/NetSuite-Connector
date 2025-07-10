
import json
import logging
from typing import Any, Optional

from .OAuth2 import NetSuiteOAuth2, OAuth2Config
from .NetSuite import NetsuiteObject

log = logging.getLogger(__name__)


class NetSuiteOAuth2Client:
    """
    NetSuite OAuth 2.0 client wrapper that provides the same interface as the original NetSuite class
    but uses OAuth 2.0 M2M authentication instead of OAuth 1.0 TBA.
    
    Usage:
    ```python
    from NetSuite_Connector.NetSuiteOAuth2Client import NetSuiteOAuth2Client
    
    client = NetSuiteOAuth2Client(
        account_id="123456",
        client_id="your_client_id",
        certificate_id="your_certificate_id",
        private_key="-----BEGIN PRIVATE KEY-----\n....\n-----END PRIVATE KEY-----"
    )
    
    response = client.get(
        url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
        headers={"Content-Type": "application/json"}
    )
    ```
    """
    
    def __init__(
        self,
        account_id: str,
        client_id: str,
        certificate_id: str,
        private_key: str,
        scope: str = "restlets,rest_webservices"
    ):
        config = OAuth2Config(
            account_id=account_id,
            client_id=client_id,
            certificate_id=certificate_id,
            private_key=private_key,
            scope=scope
        )
        self.oauth2_client = NetSuiteOAuth2(config)
        self.account_id = account_id
    
    def get(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None) -> NetsuiteObject:
        """Make a GET request to NetSuite REST API."""
        return self.oauth2_client.make_authenticated_request(
            method="GET",
            url=url,
            headers=headers,
            params=params
        )
    
    def post(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        body: Optional[Any] = None
    ) -> NetsuiteObject:
        """Make a POST request to NetSuite REST API."""
        if isinstance(body, (dict, list)):
            return self.oauth2_client.make_authenticated_request(
                method="POST",
                url=url,
                headers=headers,
                params=params,
                json_data=body
            )
        else:
            return self.oauth2_client.make_authenticated_request(
                method="POST",
                url=url,
                headers=headers,
                params=params,
                data=body
            )
    
    def put(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        body: Optional[Any] = None
    ) -> NetsuiteObject:
        """Make a PUT request to NetSuite REST API."""
        if isinstance(body, (dict, list)):
            return self.oauth2_client.make_authenticated_request(
                method="PUT",
                url=url,
                headers=headers,
                params=params,
                json_data=body
            )
        else:
            return self.oauth2_client.make_authenticated_request(
                method="PUT",
                url=url,
                headers=headers,
                params=params,
                data=body
            )
    
    def delete(self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None) -> NetsuiteObject:
        """Make a DELETE request to NetSuite REST API."""
        return self.oauth2_client.make_authenticated_request(
            method="DELETE",
            url=url,
            headers=headers,
            params=params
        )
