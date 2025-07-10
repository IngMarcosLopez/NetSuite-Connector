
import json
import logging
import traceback
from typing import Any, Optional

import requests

from .OAuth2 import NetSuiteOAuth2, OAuth2Config
from .NetSuite import NetsuiteObject

log = logging.getLogger(__name__)


class NetSuiteOAuth2Client:
    """
    OAuth 2.0 client for NetSuite REST API operations.
    
    Usage:
    ```python
    client = NetSuiteOAuth2Client(
        account_id="123456",
        client_id="your_client_id",
        certificate_id="your_certificate_id",
        private_key="-----BEGIN PRIVATE KEY-----\n....\n-----END PRIVATE KEY-----"
    )
    
    response = client.get(url="https://xxxx.restlets.api.netsuite.com/...", headers={"Content-Type": "application/json"})
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
        self.account_id = account_id
        config = OAuth2Config(
            account_id=account_id,
            client_id=client_id,
            certificate_id=certificate_id,
            private_key=private_key,
            scope=scope
        )
        self.oauth2_client = NetSuiteOAuth2(config)
    
    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        body: Optional[Any] = None
    ) -> NetsuiteObject:
        """Make an authenticated request to NetSuite."""
        response = NetsuiteObject(url=url, request_headers=headers, request_data=body)
        
        try:
            # Get access token
            access_token = self.oauth2_client.get_access_token()
            
            # Prepare headers
            if headers is None:
                headers = {}
            headers["Authorization"] = f"Bearer {access_token}"
            
            # Prepare request data
            request_kwargs = {
                "url": url,
                "headers": headers,
                "params": params
            }
            
            if body is not None:
                if isinstance(body, dict):
                    request_kwargs["json"] = body
                else:
                    request_kwargs["data"] = body
            
            # Make request
            req = requests.request(method, **request_kwargs)
            
            response.response = req.text
            response.code = req.status_code
            response.request_headers = headers
            
        except Exception as e:
            log.error(f"Error making {method} request: {str(e)}")
            log.error(traceback.format_exc())
            response.response = f"Error: {str(e)}"
            response.code = 500
            
        return response
    
    def get(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> NetsuiteObject:
        """Make a GET request."""
        return self._make_request("GET", url, headers, params)
    
    def post(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        body: Optional[Any] = None
    ) -> NetsuiteObject:
        """Make a POST request."""
        return self._make_request("POST", url, headers, params, body)
    
    def put(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        body: Optional[Any] = None
    ) -> NetsuiteObject:
        """Make a PUT request."""
        return self._make_request("PUT", url, headers, params, body)
    
    def delete(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> NetsuiteObject:
        """Make a DELETE request."""
        return self._make_request("DELETE", url, headers, params)
