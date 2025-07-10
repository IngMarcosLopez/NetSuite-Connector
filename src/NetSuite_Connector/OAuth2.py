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

    def __post_init__(self):
        """Validate and format account ID according to NetSuite requirements."""
        if not self.account_id:
            raise ValueError("Account ID is required")

        # Account ID should be in format like TSTDRV123456 or 123456_SB1
        # For REST endpoints, we need to format it properly (lowercase with hyphens)
        self.formatted_account_id = self.account_id.lower().replace("_", "-")


class NetSuiteOAuth2:
    """
    NetSuite OAuth 2.0 client using JWT client assertion.
    """

    def __init__(self, config: OAuth2Config):
        self.config = config
        self._access_token = None
        self._token_expires_at = None

    def _create_jwt_assertion(self) -> str:
        """Create JWT client assertion for OAuth 2.0 token request."""
        # JWT Header
        header = {"alg": "RS256", "typ": "JWT", "kid": self.config.certificate_id}

        # JWT Payload - Updated to use formatted_account_id for token endpoint
        now = int(time.time())
        payload = {
            "iss": self.config.client_id,
            "sub": self.config.client_id,
            "aud": f"https://{self.config.formatted_account_id}.suitetalk.api.netsuite.com/services/rest/auth/oauth2/v1/token",
            "exp": now + 300,  # 5 minutes from now
            "iat": now,
            "jti": secrets.token_hex(16),
        }

        # Encode header and payload
        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header).encode("utf-8")
        ).decode("utf-8").rstrip('=')
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(payload).encode("utf-8")
        ).decode("utf-8").rstrip('=')

        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = self._sign_message(message)

        return f"{message}.{signature}"

    def _sign_message(self, message: str) -> str:
        """Sign message with private key."""
        # Load private key
        private_key = serialization.load_pem_private_key(
            self.config.private_key.encode("utf-8"),
            password=None,
            backend=default_backend(),
        )

        # Sign message
        signature = private_key.sign(
            message.encode("utf-8"), 
            padding.PKCS1v15(), 
            hashes.SHA256()
        )

        return base64.urlsafe_b64encode(signature).decode("utf-8").rstrip('=')

    def get_access_token(self) -> str:
        """Get access token using JWT client assertion."""
        # Check if token is still valid
        if self._access_token and self._token_expires_at and time.time() < self._token_expires_at:
            return self._access_token

        try:
            # Create JWT assertion
            jwt_assertion = self._create_jwt_assertion()

            # Token request - Updated to use formatted_account_id
            token_url = f"https://{self.config.formatted_account_id}.suitetalk.api.netsuite.com/services/rest/auth/oauth2/v1/token"

            data = {
                "grant_type": "client_credentials",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": jwt_assertion,
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }

            response = requests.post(token_url, data=data, headers=headers, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data["access_token"]
            # Set expiration with some buffer
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in - 60  # 1 minute buffer

            return self._access_token

        except Exception as e:
            log.error(f"Error getting access token: {str(e)}")
            log.error(traceback.format_exc())
            raise

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