# Standard Python Libraries
import base64
from dataclasses import dataclass
import json
import logging
import secrets
import time
import traceback
from typing import Any

# Third-Party Libraries
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import requests

from .NetSuite import NetsuiteObject

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@dataclass
class OAuth2Config:
    account_id: str
    client_id: str
    certificate_id: str
    private_key: str  # PEM format private key
    scope: str = "restlets,rest_webservices"


class NetSuiteOAuth2:
    """
    NetSuite OAuth 2.0 Machine-to-Machine (M2M) authentication using private key and certificate ID.

    Usage:
    ```python
    from NetSuite_Connector.OAuth2 import NetSuiteOAuth2, OAuth2Config

    config = OAuth2Config(
        account_id="123456",
        client_id="your_client_id",
        certificate_id="your_certificate_id",
        private_key="-----BEGIN PRIVATE KEY-----\n....\n-----END PRIVATE KEY-----",
        scope="restlets,rest_webservices"
    )

    oauth2_client = NetSuiteOAuth2(config)
    token = oauth2_client.get_access_token()
    ```
    """

    def __init__(self, config: OAuth2Config):
        self.config = config
        self.access_token = None
        self.token_expires_at = None
        self._private_key = None
        self._load_private_key()

    def _load_private_key(self):
        """Load the private key from PEM format string."""
        try:
            self._private_key = serialization.load_pem_private_key(
                self.config.private_key.encode(),
                password=None,
                backend=default_backend(),
            )
        except Exception as e:
            log.error(f"Failed to load private key: {e}")
            raise ValueError("Invalid private key format") from e

    def _create_jwt_assertion(self) -> str:
        """Create JWT assertion for OAuth 2.0 client credentials flow."""
        now = int(time.time())

        # JWT Header
        header = {"alg": "RS256", "typ": "JWT", "kid": self.config.certificate_id}

        # JWT Payload
        payload = {
            "iss": self.config.client_id,
            "sub": self.config.client_id,
            "aud": "https://system.netsuite.com/app/login/oauth2/token.nl",
            "iat": now,
            "exp": now + 300,  # 5 minutes expiration
            "jti": secrets.token_urlsafe(32),
        }

        # Encode header and payload
        header_encoded = (
            base64.urlsafe_b64encode(json.dumps(header, separators=(",", ":")).encode())
            .decode()
            .rstrip("=")
        )

        payload_encoded = (
            base64.urlsafe_b64encode(
                json.dumps(payload, separators=(",", ":")).encode()
            )
            .decode()
            .rstrip("=")
        )

        # Create signing input
        signing_input = f"{header_encoded}.{payload_encoded}"

        # Sign with private key
        signature = self._private_key.sign(
            signing_input.encode(), padding.PKCS1v15(), hashes.SHA256()
        )

        signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{signing_input}.{signature_encoded}"

    def get_access_token(self) -> str | None:
        """Get access token using OAuth 2.0 client credentials flow."""
        # Check if we have a valid token
        if (
            self.access_token
            and self.token_expires_at
            and time.time() < self.token_expires_at
        ):
            return self.access_token

        try:
            # Create JWT assertion
            assertion = self._create_jwt_assertion()

            # Token endpoint
            token_url = "https://system.netsuite.com/app/login/oauth2/token.nl"

            # Request parameters
            data = {
                "grant_type": "client_credentials",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": assertion,
                "scope": self.config.scope,
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }

            log.debug(f"Requesting token from {token_url}")
            response = requests.post(token_url, data=data, headers=headers, timeout=300)

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = (
                    time.time() + expires_in - 60
                )  # Refresh 1 minute early
                log.debug("Successfully obtained access token")
                return self.access_token
            log.error(f"Token request failed: {response.status_code} - {response.text}")
            return None

        except Exception as e:
            log.error(f"Failed to get access token: {e}")
            log.error(traceback.format_exc())
            return None

    def make_authenticated_request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: Any | None = None,
        json_data: dict | None = None,
    ) -> NetsuiteObject:
        """Make an authenticated request to NetSuite REST API."""
        token = self.get_access_token()
        if not token:
            response = NetsuiteObject(
                url=url, request_headers=headers, request_data=data
            )
            response.code = 401
            response.response = "Failed to obtain access token"
            return response

        # Add authorization header
        if headers is None:
            headers = {}
        headers["Authorization"] = f"Bearer {token}"

        response = NetsuiteObject(
            url=url, request_headers=headers, request_data=data or json_data
        )

        try:
            log.debug(f"Making {method} request to {url}")
            log.debug(f"Headers: {json.dumps(headers)}")

            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=300,
            )

            response.response = resp.text
            response.code = resp.status_code
            log.debug(f"Response status: {resp.status_code}")

        except Exception as e:
            log.error(f"Request failed: {e}")
            log.error(traceback.format_exc())
            response.code = 500
            response.response = str(e)

        return response
