import json
import logging
import traceback
from typing import Any

import requests
import requests_oauthlib as oauth

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class NetSuite(object):
    """
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
    """

    def __init__(self, account_id: Any, consumer_keys: dict, token_keys: dict) -> None:
        self.oauth_version = "1.0"
        self.signature_method = "HMAC-SHA256"
        self.account_id = account_id
        self.consumer_key = (
            consumer_keys["consumer_key"]
            if consumer_keys and "consumer_key" in consumer_keys
            else None
        )
        self.consumer_secret = (
            consumer_keys["consumer_secret"]
            if consumer_keys and "consumer_secret" in consumer_keys
            else None
        )
        self.token_id = (
            token_keys["token_key"]
            if token_keys and "token_key" in token_keys
            else None
        )
        self.token_secret = (
            token_keys["token_secret"]
            if token_keys and "token_secret" in token_keys
            else None
        )

    def _make_request_session(self) -> oauth.OAuth1Session:
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
        headers: dict = {},
        params: dict = {},
        body: dict = {},
    ) -> requests.Response:
        try:
            self._request_session = self._make_request_session()
            log.debug(
                f"Making request to restlet at {url}. Payload {body}. "
                f"Headers: {json.dumps(headers)}"
            )
            method = getattr(self._request_session, http_method.lower())
            resp = method(
                url,
                data=(
                    json.dumps(body)
                    if isinstance(body, dict) or isinstance(body, list)
                    else body
                ),
                params=params,
                headers=headers,
            )
            log.debug(f"Got response headers: {json.dumps(dict(resp.headers))}")
            response = {
                "url": url,
                "request_headers": headers,
                "request_data": body,
                "response": resp.text,
                "code": resp.status_code,
            }
        except:
            log.warning(traceback.format_exc())
            response = {"code": 500, "response": traceback.format_exc()}
        return NetsuiteObject(response)

    def get(self, **kwargs) -> requests.Response:
        return self._make_request(http_method="GET", **kwargs)

    def put(self, **kwargs) -> requests.Response:
        return self._make_request(http_method="PUT", **kwargs)

    def post(self, **kwargs) -> requests.Response:
        return self._make_request(http_method="POST", **kwargs)

    def delete(self, **kwargs) -> requests.Response:
        return self._make_request(http_method="DELETE", **kwargs)


class NetsuiteObject(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(
                    self,
                    a,
                    [NetsuiteObject(x) if isinstance(x, dict) else x for x in b],
                )
            else:
                setattr(self, a, NetsuiteObject(b) if isinstance(b, dict) else b)
