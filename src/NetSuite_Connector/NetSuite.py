import json
import logging
import traceback
from dataclasses import asdict, dataclass
from typing import Any, Optional

import requests_oauthlib as oauth

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@dataclass
class NetsuiteObject:
    url: Optional[str] = None
    request_headers: Optional[dict] = None
    request_data: Optional[dict | str] = None
    response: str = None
    code: int = None

    def __repr__(self):
        return f"NetsuiteObject(url={self.url}, request_headers={self.request_headers}, request_data={self.request_data}, response={self.response}, code={self.code})"

    @property
    def json(self):
        return asdict(self)


class NetSuite(object):
    """
    The NetSuite class is a Python wrapper for the NetSuite REST API. It provides methods for making HTTP requests to the NetSuite REST API using OAuth 1.0 authentication. The class supports GET, PUT, POST, and DELETE HTTP methods. The class also provides error handling for failed requests.
    ```
    from NetSuite_Connector.NetSuite import NetSuite
    nt = NetSuite(
        account_id=123456,
        consumer_keys=dict(consumer_key="2345678", consumer_secret="3456yhg"),
        token_keys=dict(token_key="wfdbfdsdfg", token_secret="efguhfjoidejhfije"),
    )

    x = nt.get(
        url="https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx",
        headers={"Content-Type": "application/json"},
        params={}
    )
    print(x)
    # NetsuiteObject(url='https://xxxx.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=xxxx&deploy=xxxx', request_headers={'Content-Type': 'application/json'}, response='{"foo":"bar"}', code=200)
    ```
    """

    def __init__(self, account_id: Any, consumer_keys: dict, token_keys: dict) -> None:
        self.oauth_version = "1.0"
        self.signature_method = "HMAC-SHA256"
        self.account_id = account_id
        self.consumer_key, self.consumer_secret = self._validate_keys(
            consumer_keys, ["consumer_key", "consumer_secret"]
        ).values()
        self.token_id, self.token_secret = self._validate_keys(
            token_keys, ["token_key", "token_secret"]
        ).values()
        self._request_session = None

    def _validate_keys(self, keys: dict, key_names: list) -> dict:
        missing_keys = [k for k in key_names if k not in keys]
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")
        return {k: keys[k] for k in key_names}

    def _make_request_session(self) -> oauth.OAuth1Session:
        """
        Creates an OAuth1Session object for making requests to the NetSuite REST API.
        """
        return oauth.OAuth1Session(
            signature_method=self.signature_method,
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.token_id,
            resource_owner_secret=self.token_secret,
            realm=self.account_id,
        )

    def _make_request(
        self,
        http_method: str,
        url: str,
        headers: dict[str, str] = {},
        params: dict[str, Any] = {},
        body: dict[str, Any] = {},
    ) -> NetsuiteObject:
        """
        Makes an HTTP request to the NetSuite REST API using the specified HTTP method, URL, headers, parameters, and body. Returns a NetsuiteObject containing the response data.
        """
        log.debug("Making request to restlet at %s.", url)
        log.debug("Payload: %s", body)
        log.debug("Headers: %s", json.dumps(headers))
        response = NetsuiteObject(url=url, request_headers=headers, request_data=body)
        try:
            self._request_session = self._make_request_session()

            method = getattr(self._request_session, http_method.lower())
            resp = method(
                url,
                data=(json.dumps(body) if isinstance(body, (dict, list)) else body),
                params=params,
                headers=headers,
            )
            log.debug("Got response headers: %s", json.dumps(dict(resp.headers)))
            response.response = resp.text
            response.code = resp.status_code
        except Exception:
            log.warning(traceback.format_exc())
            response.code = 500
            response.response = traceback.format_exc()
        return response

    def get(self, **kwargs) -> NetsuiteObject:
        """
        Makes a GET request to the NetSuite REST API using the specified URL, headers, and parameters. Returns a NetsuiteObject containing the response data.
        """
        return self._make_request(http_method="GET", **kwargs)

    def put(self, **kwargs) -> NetsuiteObject:
        """
        Makes a PUT request to the NetSuite REST API using the specified URL, headers, parameters, and body. Returns a NetsuiteObject containing the response data.
        """
        return self._make_request(http_method="PUT", **kwargs)

    def post(self, **kwargs) -> NetsuiteObject:
        """
        Makes a POST request to the NetSuite REST API using the specified URL, headers, parameters, and body. Returns a NetsuiteObject containing the response data.
        """
        return self._make_request(http_method="POST", **kwargs)

    def delete(self, **kwargs) -> NetsuiteObject:
        """
        Makes a DELETE request to the NetSuite REST API using the specified URL, headers, and parameters. Returns a NetsuiteObject containing the response data.
        """
        return self._make_request(http_method="DELETE", **kwargs)
