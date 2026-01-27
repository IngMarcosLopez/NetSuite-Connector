"""
Tests for ODBC module.
"""
import json
import pytest
import sys
sys.path.insert(0, "/home/runner/workspace/src")

from NetSuite_Connector.ODBC import ODBC
from NetSuite_Connector.NetSuite import NetsuiteObject


class TestODBCInstantiation:
    """Tests for ODBC class instantiation."""
    
    def test_instantiation_with_valid_keys(self):
        """ODBC can be instantiated with valid credentials."""
        account_id = "123456"
        consumer_keys = {"consumer_key": "2345678", "consumer_secret": "3456yhg"}
        token_keys = {"token_key": "wfdbfdsdfg", "token_secret": "efguhfjoidejhfije"}

        odbc = ODBC(account_id, consumer_keys, token_keys)

        assert odbc.account_id == account_id
        assert odbc.consumer_key == consumer_keys["consumer_key"]
        assert odbc.consumer_secret == consumer_keys["consumer_secret"]
        assert odbc.token_id == token_keys["token_key"]
        assert odbc.token_secret == token_keys["token_secret"]

    def test_instantiation_with_missing_consumer_secret(self):
        """ODBC raises ValueError if consumer_secret is missing."""
        account_id = 123456
        consumer_keys = {"consumer_key": "2345678"}
        token_keys = {"token_key": "wfdbfdsdfg", "token_secret": "efguhfjoidejhfije"}

        with pytest.raises(ValueError):
            ODBC(account_id, consumer_keys, token_keys)
    
    def test_instantiation_with_missing_token_secret(self):
        """ODBC raises ValueError if token_secret is missing."""
        account_id = 123456
        consumer_keys = {"consumer_key": "ck", "consumer_secret": "cs"}
        token_keys = {"token_key": "tk"}

        with pytest.raises(ValueError):
            ODBC(account_id, consumer_keys, token_keys)
    
    def test_instantiation_with_missing_consumer_key(self):
        """ODBC raises ValueError if consumer_key is missing."""
        account_id = 123456
        consumer_keys = {"consumer_secret": "cs"}
        token_keys = {"token_key": "tk", "token_secret": "ts"}

        with pytest.raises(ValueError):
            ODBC(account_id, consumer_keys, token_keys)
    
    def test_instantiation_with_missing_token_key(self):
        """ODBC raises ValueError if token_key is missing."""
        account_id = 123456
        consumer_keys = {"consumer_key": "ck", "consumer_secret": "cs"}
        token_keys = {"token_secret": "ts"}

        with pytest.raises(ValueError):
            ODBC(account_id, consumer_keys, token_keys)


class TestODBCSuiteQLEndpoint:
    """Tests for ODBC SuiteQL endpoint construction."""
    
    def test_suiteql_endpoint_with_underscore(self):
        """Test endpoint is constructed correctly with underscore account ID."""
        odbc = ODBC(
            account_id="123456_SB1",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        expected = "https://123456-sb1.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
        assert odbc.suiteql_endpoint == expected
    
    def test_suiteql_endpoint_without_underscore(self):
        """Test endpoint with simple account ID."""
        odbc = ODBC(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        expected = "https://123456.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
        assert odbc.suiteql_endpoint == expected
    
    def test_suiteql_endpoint_uppercase_account_id(self):
        """Test endpoint converts uppercase account ID to lowercase."""
        odbc = ODBC(
            account_id="TSTDRV123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        assert "tstdrv123456" in odbc.suiteql_endpoint


class TestODBCQuery:
    """Tests for ODBC query method."""
    
    def test_query_returns_netsuite_object(self, requests_mock):
        """Test query method returns NetsuiteObject."""
        odbc = ODBC(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        response_data = {"items": [{"id": "1", "name": "Test"}]}
        requests_mock.post(odbc.suiteql_endpoint, json=response_data, status_code=200)
        
        result = odbc.query("SELECT * FROM customer")
        
        assert isinstance(result, NetsuiteObject)
        assert result.code == 200
    
    def test_query_sets_request_data(self, requests_mock):
        """Test query method sets request_data correctly."""
        odbc = ODBC(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        requests_mock.post(odbc.suiteql_endpoint, json={}, status_code=200)
        
        query = "SELECT TOP 10 * FROM transaction"
        result = odbc.query(query)
        
        assert result.request_data == query
    
    def test_query_handles_success_response(self, requests_mock):
        """Test query handles successful response."""
        odbc = ODBC(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        response_data = {
            "items": [
                {"id": "1", "companyname": "Acme Corp"},
                {"id": "2", "companyname": "Tech Inc"}
            ],
            "hasMore": False,
            "totalResults": 2
        }
        requests_mock.post(odbc.suiteql_endpoint, json=response_data, status_code=200)
        
        result = odbc.query("SELECT id, companyname FROM customer")
        
        assert result.code == 200
        parsed = json.loads(result.response)
        assert len(parsed["items"]) == 2
    
    def test_query_handles_error_response(self, requests_mock):
        """Test query handles error response."""
        odbc = ODBC(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        error_data = {
            "type": "error",
            "code": "INVALID_SEARCH",
            "message": "Invalid SQL query"
        }
        requests_mock.post(odbc.suiteql_endpoint, json=error_data, status_code=400)
        
        result = odbc.query("SELECT * FROM invalid_table")
        
        assert result.code == 400
    
    def test_query_handles_exception(self, requests_mock):
        """Test query handles exceptions gracefully."""
        odbc = ODBC(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        requests_mock.post(odbc.suiteql_endpoint, exc=Exception("Network error"))
        
        result = odbc.query("SELECT * FROM customer")
        
        assert result.code == 500
        assert "Network error" in result.response or "Exception" in result.response
    
    def test_query_with_complex_sql(self, requests_mock):
        """Test query with complex SQL statement."""
        odbc = ODBC(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        response_data = {"items": [], "totalResults": 0}
        requests_mock.post(odbc.suiteql_endpoint, json=response_data, status_code=200)
        
        complex_query = """
            SELECT t.tranid, t.trandate, c.companyname, t.total
            FROM transaction t
            INNER JOIN customer c ON t.entity = c.id
            WHERE t.trandate >= '2024-01-01'
            ORDER BY t.trandate DESC
        """
        result = odbc.query(complex_query)
        
        assert result.code == 200
    
    def test_query_sends_correct_headers(self, requests_mock):
        """Test query sends correct headers."""
        odbc = ODBC(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        requests_mock.post(odbc.suiteql_endpoint, json={}, status_code=200)
        
        odbc.query("SELECT 1")
        
        history = requests_mock.request_history
        assert len(history) == 1
        assert "prefer" in history[0].headers
        prefer_value = history[0].headers["prefer"]
        if isinstance(prefer_value, bytes):
            prefer_value = prefer_value.decode()
        assert prefer_value == "transient"


class TestODBCInheritance:
    """Tests for ODBC inheritance from NetSuite."""
    
    def test_inherits_from_netsuite(self):
        """Test ODBC inherits from NetSuite class."""
        from NetSuite_Connector.NetSuite import NetSuite
        
        assert issubclass(ODBC, NetSuite)
    
    def test_has_netsuite_methods(self):
        """Test ODBC has all NetSuite methods."""
        odbc = ODBC(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        assert hasattr(odbc, 'get')
        assert hasattr(odbc, 'post')
        assert hasattr(odbc, 'put')
        assert hasattr(odbc, 'delete')
        assert callable(odbc.get)
        assert callable(odbc.post)
