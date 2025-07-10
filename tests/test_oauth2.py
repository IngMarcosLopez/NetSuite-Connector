# Standard Python Libraries
from unittest.mock import Mock, patch

# Third-Party Libraries
import pytest

# NTST-CONN Libraries
from NetSuite_Connector.NetSuite import NetsuiteObject
from NetSuite_Connector.NetSuiteOAuth2Client import NetSuiteOAuth2Client
from NetSuite_Connector.OAuth2 import NetSuiteOAuth2, OAuth2Config
from NetSuite_Connector.OAuth2ODBC import OAuth2ODBC


class TestOAuth2:
    @pytest.fixture
    def oauth2_config(self):
        # Sample RSA private key for testing (generated for testing purposes only)
        private_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKB
xQOKiKQDz5PL2G9NqAjiaGXZ3u8lVKc6xLOHOxBmgZCdUXfBIL6mKoXjBnmjEjG
hKBXqjJq1t3pzxWt8LLxNgW1cHnOGcCNcvVGt8y6qRVfVKKLXhzILFMF6J8qGkQ
I4HpD7xKkgSyDiQgdJfRVbJp8lTLPGaP9nk6cPmKRJ+cL4FcEOzKDYN7VbqPKs
fQwF5J4kVJUGPGQZ+hOCfT4HHiEDJrBxXGfzKVnRKWxJJWRyHJNqWz6pLfzqQU
qnCGq6HyMq6TJLKaOsXbOTlmSjuq0NmRZJ4k3HmrXD7W4cGP5aZ2J3NdJ1dKo8
+4QqcOo+zXkJAgMBAAECggEAeXONOZRrjVuqrjWvdOdNJ6OjzBTK2dIrHSL2nCf3
zADLcGOJPmj4LQj/JnzCHKlOTLJxkwqKT1EK0YkEKJ6j2JjrJxnKaHoZRhKJgCT
7hUXjQfWkFJ3GrJXCdQq7cLjU8IFN3bKiCkPL0wqKYbXo2aR0tZvBzCBrfLqPuM
LhWzCkH6nIgDjXfIzQFcEJxD8XYEcMO9pCNYGh7HdNrL9YYXrqOqQYWjmCZgHlW
hqHXjHoZwdKbKpQ4kHxfDcDOOXEjJ3SYx/cT1YvZqZqkBnHJDwJhvCOT7YVFqYo
XjEfpL5uYpHJGdCgGJaM+zWIU3KfDVAqXGqsT8mCNJ0ZlOVKJtgfQgOKE6GzpjY
Y4wKBgQDfL0jHGsKjgbOxKYEQZQVhTvwmITkRhLKdKXhMOFmPTgRSTCIXjCxMf
eP7+0IjgmzqBEcQRvgNH3J4JH9iMhgJ3VmOHJQhZBaUg/4gQo5FJjfmJmZL+3J
5aO0BNxZGRMYLVqvkEaF+s1q7J/9w4T1NdgkGsOE7cALBJxhJFMcDKpbT8qeY0
/qJxiWQKBgQDT0dLGXgIJhYwz3GZHLsWpNJgfmB5I8YhI4wDbWFCGJNjWvZXOu
FGKMXfNKPDrOLfVgDmfzTU8GLYJm/kIdKYU5t2CvLQxdCXkQO2HcNsL4fNXQjG
2J1OJHGTjHmXqQyFJ6ZsNP4FE5WRc2pSWJgRCdLr8e6vdtlQeIHjGmQrqjy5nQ
KBgGqQRZdCjUEr1AyZqZpQJtLFMLSVEQbOGNkNRyYzLJ9+3PsKu3vWEIFpQ9VB
LQKBgQCXrXdvKHjlNXvnxgGMmhYOxSIYxXcAhyVhZGnYJVQnHQvjJJtF2gJVTpg
ZdMnP8EJqNnz+oRNPULYM7S6MxGzQWTfz9U8vQjJmzITKb6+a5kSgWV+V8kN8h
QpwQEXJGMUoNhRzLfHpOlWGtOxGXLdqzgPKgTbdL9dPqz0QKBgQCVEj1lQNnKn
2oSJ2uJQzPaVGYQKXXXJzfCQgN4kNgNbvkZJjmZKXxgRXJONJMsNkbNjMxbhpI
-----END PRIVATE KEY-----"""

        return OAuth2Config(
            account_id="TEST_ACCOUNT_123",
            client_id="test_client_id",
            certificate_id="test_certificate_id",
            private_key=private_key,
            scope="restlets,rest_webservices",
        )

    @patch("requests.post")
    def test_oauth2_token_generation(self, mock_post, oauth2_config):
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_token_response

        oauth2 = NetSuiteOAuth2(oauth2_config)
        token = oauth2.get_access_token()

        assert token == "test_access_token"
        mock_post.assert_called_once()

    @patch("requests.post")
    @patch("requests.request")
    def test_oauth2_client_get_request(self, mock_request, mock_post, oauth2_config):
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_token_response

        # Mock API response
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.text = '{"data": "test"}'
        mock_request.return_value = mock_api_response

        client = NetSuiteOAuth2Client(
            account_id=oauth2_config.account_id,
            client_id=oauth2_config.client_id,
            certificate_id=oauth2_config.certificate_id,
            private_key=oauth2_config.private_key,
        )

        response = client.get(
            url="https://test.restlets.api.netsuite.com/test",
            headers={"Content-Type": "application/json"},
        )

        assert response.code == 200
        assert response.response == '{"data": "test"}'

    @patch("requests.post")
    @patch("requests.request")
    def test_oauth2_client_post_request(self, mock_request, mock_post, oauth2_config):
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_token_response

        # Mock API response
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.text = '{"result": "success"}'
        mock_request.return_value = mock_api_response

        client = NetSuiteOAuth2Client(
            account_id=oauth2_config.account_id,
            client_id=oauth2_config.client_id,
            certificate_id=oauth2_config.certificate_id,
            private_key=oauth2_config.private_key,
        )

        body = {"test": "data"}
        response = client.post(
            url="https://test.restlets.api.netsuite.com/test",
            headers={"Content-Type": "application/json"},
            body=body,
        )

        assert response.code == 200
        assert response.response == '{"result": "success"}'

    def test_oauth2_odbc_initialization(self, oauth2_config):
        odbc = OAuth2ODBC(
            account_id=oauth2_config.account_id,
            client_id=oauth2_config.client_id,
            certificate_id=oauth2_config.certificate_id,
            private_key=oauth2_config.private_key,
        )

        expected_endpoint = f'https://{oauth2_config.account_id.lower().replace("_", "-")}.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql'
        assert odbc.suiteql_endpoint == expected_endpoint

    @patch("requests.post")
    @patch("requests.request")
    def test_oauth2_odbc_query_success(self, mock_request, mock_post, oauth2_config):
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_token_response

        # Mock SuiteQL response
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.text = (
            '{"items": [{"id": 1, "name": "test"}], "hasMore": false}'
        )
        mock_request.return_value = mock_api_response

        odbc = OAuth2ODBC(
            account_id=oauth2_config.account_id,
            client_id=oauth2_config.client_id,
            certificate_id=oauth2_config.certificate_id,
            private_key=oauth2_config.private_key,
        )

        result = odbc.query("SELECT TOP 10 * FROM transaction")

        assert isinstance(result, NetsuiteObject)
        assert result.code == 200
        assert '"items"' in result.response

    @patch("requests.post")
    @patch("requests.request")
    def test_oauth2_odbc_query_error(self, mock_request, mock_post, oauth2_config):
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_token_response

        # Mock error response
        mock_api_response = Mock()
        mock_api_response.status_code = 400
        mock_api_response.text = '{"error": "Invalid query"}'
        mock_request.return_value = mock_api_response

        odbc = OAuth2ODBC(
            account_id=oauth2_config.account_id,
            client_id=oauth2_config.client_id,
            certificate_id=oauth2_config.certificate_id,
            private_key=oauth2_config.private_key,
        )

        result = odbc.query("INVALID SQL")

        assert isinstance(result, NetsuiteObject)
        assert result.code == 400
        assert '"error"' in result.response

    def test_oauth2_config_creation(self):
        config = OAuth2Config(
            account_id="TEST_123",
            client_id="client_123",
            certificate_id="cert_123",
            private_key="test_key",
        )

        assert config.account_id == "TEST_123"
        assert config.client_id == "client_123"
        assert config.certificate_id == "cert_123"
        assert config.private_key == "test_key"
        assert config.scope == "restlets,rest_webservices"
