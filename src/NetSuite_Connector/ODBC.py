import base64
import binascii
import hashlib
import hmac
import random

try:
    from secrets import randbits
except ImportError:
    from random import getrandbits as randbits

import time
from typing import Any

import pyodbc


class ODBC(object):
    ServiceHost = ".connect.api.netsuite.com"

    def __init__(
        self,
        account_id: Any,
        user_email: str,
        role_id: int,
        dsn: str,
        consumer_keys: dict,
        token_keys: dict,
    ) -> None:
        self.oauth_version = "1.0"
        self.signature_method = "HMAC-SHA256"
        self.account_id = account_id
        self.user = user_email
        self.role_id = role_id
        self.dsn = dsn
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

    @staticmethod
    def generate_nonce(length=20):
        """Generate pseudo-random number."""
        word_characters = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )
        return "".join(
            [
                word_characters[random.randint(0, len(word_characters))]
                for i in range(length)
            ]
        )

    @staticmethod
    def generate_timestamp():
        """Get seconds since epoch (UTC)."""
        return str(int(time.time()))

    def _make_password(self):
        base_string = "&".join(
            [
                self.account_id,
                self.consumer_key,
                self.token_id,
                self.generate_nonce(),
                self.generate_timestamp(),
            ]
        )
        signature_key = "&".join([self.consumer_secret, self.token_secret])
        digest = hmac.new(
            bytes(signature_key, "ascii"), base_string.encode(), hashlib.sha256
        ).digest()
        signature = f"{base64.b64encode(digest).decode()}&HMAC-SHA256"

        token_password = f"{base_string}&{signature}"
        return token_password

    def query(self):
        conn = pyodbc.connect(
            f"DSN={self.dsn};UID={self.user};password={self._make_password()}"
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT TABLE_NAME,COLUMN_NAME FROM OA_Columns ORDER BY TABLE_NAME ASC"
        )
        head = cur.description
        data = cur.fetchall()
        cur.close()
        conn.close()

        return head
