"""
Additional tests for MCP Tools handlers with mocked API calls.
"""
import json
import pytest
import sys
sys.path.insert(0, "/home/runner/workspace/src")

from unittest.mock import Mock, patch, MagicMock

from NetSuite_Connector.mcp_tools import MCPToolHandler
from NetSuite_Connector.NetSuite import NetSuite, NetsuiteObject
from NetSuite_Connector.ODBC import ODBC


@pytest.fixture
def mock_netsuite():
    """Create mock NetSuite client."""
    mock = Mock(spec=NetSuite)
    mock.account_id = "123456_SB1"
    return mock


@pytest.fixture
def mock_odbc():
    """Create mock ODBC client."""
    mock = Mock(spec=ODBC)
    return mock


@pytest.fixture
def handler_with_mocks(mock_netsuite, mock_odbc):
    """Create MCPToolHandler with mock clients."""
    return MCPToolHandler(mock_netsuite, mock_odbc)


class TestQueryNetsuiteHandler:
    """Tests for handle_query_netsuite with mocked ODBC."""
    
    def test_successful_query(self, handler_with_mocks, mock_odbc):
        """Test successful query execution."""
        mock_response = NetsuiteObject(
            response=json.dumps({"items": [{"id": "1"}]}),
            code=200
        )
        mock_odbc.query.return_value = mock_response
        
        result = handler_with_mocks.handle_query_netsuite({"query": "SELECT * FROM customer"})
        
        assert result["isError"] is False
        mock_odbc.query.assert_called_once_with("SELECT * FROM customer")


class TestGetRecordHandler:
    """Tests for handle_get_record with mocked NetSuite."""
    
    def test_successful_get(self, handler_with_mocks, mock_netsuite):
        """Test successful record retrieval."""
        mock_response = NetsuiteObject(
            response=json.dumps({"id": "123", "companyname": "Test"}),
            code=200
        )
        mock_netsuite.get.return_value = mock_response
        
        result = handler_with_mocks.handle_get_record({
            "record_type": "customer",
            "record_id": "123"
        })
        
        assert result["isError"] is False
        mock_netsuite.get.assert_called_once()
    
    def test_get_with_expand(self, handler_with_mocks, mock_netsuite):
        """Test record retrieval with expand option."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_netsuite.get.return_value = mock_response
        
        handler_with_mocks.handle_get_record({
            "record_type": "salesorder",
            "record_id": "456",
            "expand_sub_resources": True
        })
        
        call_args = mock_netsuite.get.call_args
        assert "expandSubResources=true" in call_args.kwargs["url"]


class TestCreateRecordHandler:
    """Tests for handle_create_record with mocked NetSuite."""
    
    def test_successful_create(self, handler_with_mocks, mock_netsuite):
        """Test successful record creation."""
        mock_response = NetsuiteObject(
            response=json.dumps({"id": "789"}),
            code=201
        )
        mock_netsuite.post.return_value = mock_response
        
        result = handler_with_mocks.handle_create_record({
            "record_type": "customer",
            "data": {"companyname": "New Company"}
        })
        
        assert result["isError"] is False
        mock_netsuite.post.assert_called_once()


class TestUpdateRecordHandler:
    """Tests for handle_update_record with mocked NetSuite."""
    
    def test_successful_update(self, handler_with_mocks, mock_netsuite):
        """Test successful record update."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_netsuite.put.return_value = mock_response
        
        result = handler_with_mocks.handle_update_record({
            "record_type": "customer",
            "record_id": "123",
            "data": {"email": "new@email.com"}
        })
        
        assert result["isError"] is False
        mock_netsuite.put.assert_called_once()


class TestDeleteRecordHandler:
    """Tests for handle_delete_record with mocked NetSuite."""
    
    def test_successful_delete(self, handler_with_mocks, mock_netsuite):
        """Test successful record deletion."""
        mock_response = NetsuiteObject(response="{}", code=204)
        mock_netsuite.delete.return_value = mock_response
        
        result = handler_with_mocks.handle_delete_record({
            "record_type": "customer",
            "record_id": "123"
        })
        
        assert result["isError"] is False
        mock_netsuite.delete.assert_called_once()


class TestCallRestletHandler:
    """Tests for handle_call_restlet with mocked NetSuite."""
    
    def test_get_request(self, handler_with_mocks, mock_netsuite):
        """Test GET restlet call."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_netsuite.get.return_value = mock_response
        
        result = handler_with_mocks.handle_call_restlet({
            "url": "https://test.restlets.api.netsuite.com/test",
            "method": "GET"
        })
        
        assert result["isError"] is False
        mock_netsuite.get.assert_called_once()
    
    def test_post_with_body(self, handler_with_mocks, mock_netsuite):
        """Test POST restlet call with body."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_netsuite.post.return_value = mock_response
        
        handler_with_mocks.handle_call_restlet({
            "url": "https://test.restlets.api.netsuite.com/test",
            "method": "POST",
            "body": {"key": "value"}
        })
        
        call_args = mock_netsuite.post.call_args
        assert call_args.kwargs["body"] == {"key": "value"}
    
    def test_with_params(self, handler_with_mocks, mock_netsuite):
        """Test restlet call with query params."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_netsuite.get.return_value = mock_response
        
        handler_with_mocks.handle_call_restlet({
            "url": "https://test.restlets.api.netsuite.com/test",
            "method": "GET",
            "params": {"page": "1"}
        })
        
        call_args = mock_netsuite.get.call_args
        assert call_args.kwargs["params"] == {"page": "1"}
    
    def test_put_request(self, handler_with_mocks, mock_netsuite):
        """Test PUT restlet call."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_netsuite.put.return_value = mock_response
        
        handler_with_mocks.handle_call_restlet({
            "url": "https://test.restlets.api.netsuite.com/test",
            "method": "PUT",
            "body": {"update": "data"}
        })
        
        mock_netsuite.put.assert_called_once()
    
    def test_delete_request(self, handler_with_mocks, mock_netsuite):
        """Test DELETE restlet call."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_netsuite.delete.return_value = mock_response
        
        handler_with_mocks.handle_call_restlet({
            "url": "https://test.restlets.api.netsuite.com/test",
            "method": "DELETE"
        })
        
        mock_netsuite.delete.assert_called_once()


class TestListRecordsHandler:
    """Tests for handle_list_records with mocked NetSuite."""
    
    def test_basic_list(self, handler_with_mocks, mock_netsuite):
        """Test basic record listing."""
        mock_response = NetsuiteObject(
            response=json.dumps({"items": []}),
            code=200
        )
        mock_netsuite.get.return_value = mock_response
        
        result = handler_with_mocks.handle_list_records({
            "record_type": "customer"
        })
        
        assert result["isError"] is False
    
    def test_list_with_pagination(self, handler_with_mocks, mock_netsuite):
        """Test listing with limit and offset."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_netsuite.get.return_value = mock_response
        
        handler_with_mocks.handle_list_records({
            "record_type": "invoice",
            "limit": 50,
            "offset": 100
        })
        
        call_args = mock_netsuite.get.call_args
        assert call_args.kwargs["params"]["limit"] == "50"
        assert call_args.kwargs["params"]["offset"] == "100"
    
    def test_list_with_fields(self, handler_with_mocks, mock_netsuite):
        """Test listing with specific fields."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_netsuite.get.return_value = mock_response
        
        handler_with_mocks.handle_list_records({
            "record_type": "customer",
            "fields": ["id", "companyname", "email"]
        })
        
        call_args = mock_netsuite.get.call_args
        assert call_args.kwargs["params"]["fields"] == "id,companyname,email"


class TestRunSavedSearchHandler:
    """Tests for handle_run_saved_search with mocked ODBC."""
    
    def test_basic_search(self, handler_with_mocks, mock_odbc):
        """Test running a saved search."""
        mock_response = NetsuiteObject(
            response=json.dumps({"items": []}),
            code=200
        )
        mock_odbc.query.return_value = mock_response
        
        result = handler_with_mocks.handle_run_saved_search({
            "search_id": "customsearch_123"
        })
        
        assert result["isError"] is False
    
    def test_search_with_filters(self, handler_with_mocks, mock_odbc):
        """Test saved search with additional filters."""
        mock_response = NetsuiteObject(response="{}", code=200)
        mock_odbc.query.return_value = mock_response
        
        handler_with_mocks.handle_run_saved_search({
            "search_id": "123",
            "filters": {"status": "open", "type": "invoice"}
        })
        
        call_args = mock_odbc.query.call_args[0][0]
        assert "WHERE" in call_args
        assert "status = 'open'" in call_args


class TestToolHandlerExceptionHandling:
    """Tests for exception handling in tool handlers."""
    
    def test_call_tool_catches_exception(self, handler_with_mocks, mock_odbc):
        """Test call_tool catches and formats exceptions."""
        mock_odbc.query.side_effect = Exception("Database error")
        
        result = handler_with_mocks.call_tool("query_netsuite", {"query": "SELECT 1"})
        
        assert result["isError"] is True
        content = json.loads(result["content"][0]["text"])
        assert "error" in content
