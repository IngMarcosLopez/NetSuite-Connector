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
    request_data: Optional[dict] = None
    response: str = None
    code: int = None

    @property
    def json(self):
        return asdict(self)


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
        self._request_session = None

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
    ) -> NetsuiteObject:
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
        return self._make_request(http_method="GET", **kwargs)

    def put(self, **kwargs) -> NetsuiteObject:
        return self._make_request(http_method="PUT", **kwargs)

    def post(self, **kwargs) -> NetsuiteObject:
        return self._make_request(http_method="POST", **kwargs)

    def delete(self, **kwargs) -> NetsuiteObject:
        return self._make_request(http_method="DELETE", **kwargs)
