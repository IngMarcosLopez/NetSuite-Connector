import base64
import hashlib
import hmac
import random
import time
import traceback
from typing import Any

import pandas as pd
import pyodbc

from .NetSuite import NetsuiteObject


class ODBC(object):
    ServiceHost = ".connect.api.netsuite.com"

    def __init__(
        self,
        account_id: Any,
        user_email: str,
        role_id: int,
        dsn: str,
        password: str = None,
        consumer_keys: dict = {},
        token_keys: dict = {},
    ) -> None:
        self.oauth_version = "1.0"
        self.signature_method = "HMAC-SHA256"
        self.account_id = account_id
        self.user = user_email
        self.role_id = role_id
        self.dsn = dsn
        self.password = password
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
                word_characters[random.randint(0, len(word_characters) - 1)]
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

    def query(self, query: str) -> dict:
        """
        Perfom a query to ODBC driver
        query: fully qualified sql query
        """
        try:

            conn_str = f"DSN={self.dsn};LogonID={self.user};PWD={self.password};RoleID:{self.role_id}"
            conn = pyodbc.connect(conn_str)
            cur = conn.cursor()
            cur.execute(query)
            head = cur.description
            data = cur.fetchall()
            cur.close()
            conn.close()

            df = pd.DataFrame(
                data=[tuple(x) for x in data], columns=[i[0] for i in head]
            )
            response = {
                "status": 200,
                "data_received": query,
                "columns": [i[0] for i in head],
                "response": df.to_json(orient="records"),
            }
        except Exception:
            response = {
                "status": 500,
                "data_received": query,
                "response": traceback.format_exc(),
            }
        return NetsuiteObject(response)
