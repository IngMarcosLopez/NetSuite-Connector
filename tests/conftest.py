"""
Shared test fixtures for NetSuite Connector tests.
"""
import json
import pytest
import sys
sys.path.insert(0, "/home/runner/workspace/src")

from NetSuite_Connector.NetSuite import NetSuite, NetsuiteObject
from NetSuite_Connector.ODBC import ODBC
from NetSuite_Connector.mcp_config import NetSuiteConfig
from NetSuite_Connector.mcp_server import NetSuiteMCPServer
from NetSuite_Connector.mcp_tools import MCPToolHandler


@pytest.fixture
def sample_config():
    """Sample NetSuite configuration for testing."""
    return NetSuiteConfig(
        account_id="123456_SB1",
        consumer_key="test_consumer_key",
        consumer_secret="test_consumer_secret",
        token_key="test_token_key",
        token_secret="test_token_secret"
    )


@pytest.fixture
def sample_consumer_keys():
    """Sample consumer keys dict."""
    return {
        "consumer_key": "test_consumer_key",
        "consumer_secret": "test_consumer_secret"
    }


@pytest.fixture
def sample_token_keys():
    """Sample token keys dict."""
    return {
        "token_key": "test_token_key",
        "token_secret": "test_token_secret"
    }


@pytest.fixture
def netsuite_client(sample_consumer_keys, sample_token_keys):
    """NetSuite client instance for testing."""
    return NetSuite(
        account_id="123456_SB1",
        consumer_keys=sample_consumer_keys,
        token_keys=sample_token_keys
    )


@pytest.fixture
def odbc_client(sample_consumer_keys, sample_token_keys):
    """ODBC client instance for testing."""
    return ODBC(
        account_id="123456_SB1",
        consumer_keys=sample_consumer_keys,
        token_keys=sample_token_keys
    )


@pytest.fixture
def mcp_server(sample_consumer_keys, sample_token_keys):
    """MCP Server instance for testing."""
    return NetSuiteMCPServer(
        account_id="123456_SB1",
        consumer_keys=sample_consumer_keys,
        token_keys=sample_token_keys
    )


@pytest.fixture
def tool_handler(netsuite_client, odbc_client):
    """MCP Tool Handler instance for testing."""
    return MCPToolHandler(netsuite_client, odbc_client)


@pytest.fixture
def mock_success_response():
    """Mock successful NetSuite response."""
    return NetsuiteObject(
        url="https://test.suitetalk.api.netsuite.com/test",
        request_headers={"Content-Type": "application/json"},
        response=json.dumps({"items": [{"id": "1", "name": "Test"}]}),
        code=200
    )


@pytest.fixture
def mock_error_response():
    """Mock error NetSuite response."""
    return NetsuiteObject(
        url="https://test.suitetalk.api.netsuite.com/test",
        request_headers={"Content-Type": "application/json"},
        response=json.dumps({"error": {"message": "Not found"}}),
        code=404
    )


@pytest.fixture
def mock_customer_data():
    """Sample customer record data."""
    return {
        "id": "12345",
        "companyname": "Test Company",
        "email": "test@example.com",
        "phone": "555-1234"
    }


@pytest.fixture
def mock_invoice_data():
    """Sample invoice record data."""
    return {
        "id": "67890",
        "tranid": "INV-001",
        "entity": {"id": "12345", "refName": "Test Company"},
        "total": 1000.00,
        "status": {"id": "open", "refName": "Open"}
    }
