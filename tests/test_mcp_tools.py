"""
Tests for MCP Tools module.
"""
import json
import pytest
import sys
sys.path.insert(0, "/home/runner/workspace/src")

from unittest.mock import Mock, patch

from NetSuite_Connector.mcp_tools import (
    MCPTool,
    TOOL_SCHEMAS,
    MCPToolHandler,
    get_tool_definitions
)
from NetSuite_Connector.NetSuite import NetsuiteObject


class TestMCPTool:
    """Tests for MCPTool dataclass."""
    
    def test_tool_creation(self):
        """Test creating an MCPTool."""
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {}}
        )
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.handler is None


class TestToolSchemas:
    """Tests for TOOL_SCHEMAS definitions."""
    
    def test_all_tools_have_required_fields(self):
        """Test all tools have name, description, input_schema."""
        for name, tool in TOOL_SCHEMAS.items():
            assert tool.name == name
            assert tool.description
            assert tool.input_schema
            assert "type" in tool.input_schema
            assert "properties" in tool.input_schema
    
    def test_query_netsuite_schema(self):
        """Test query_netsuite tool schema."""
        tool = TOOL_SCHEMAS["query_netsuite"]
        assert tool.name == "query_netsuite"
        assert "query" in tool.input_schema["properties"]
        assert "query" in tool.input_schema["required"]
    
    def test_get_record_schema(self):
        """Test get_record tool schema."""
        tool = TOOL_SCHEMAS["get_record"]
        assert "record_type" in tool.input_schema["properties"]
        assert "record_id" in tool.input_schema["properties"]
        assert "record_type" in tool.input_schema["required"]
        assert "record_id" in tool.input_schema["required"]
    
    def test_create_record_schema(self):
        """Test create_record tool schema."""
        tool = TOOL_SCHEMAS["create_record"]
        assert "record_type" in tool.input_schema["properties"]
        assert "data" in tool.input_schema["properties"]
    
    def test_update_record_schema(self):
        """Test update_record tool schema."""
        tool = TOOL_SCHEMAS["update_record"]
        required = tool.input_schema["required"]
        assert "record_type" in required
        assert "record_id" in required
        assert "data" in required
    
    def test_delete_record_schema(self):
        """Test delete_record tool schema."""
        tool = TOOL_SCHEMAS["delete_record"]
        assert "record_type" in tool.input_schema["required"]
        assert "record_id" in tool.input_schema["required"]
    
    def test_call_restlet_schema(self):
        """Test call_restlet tool schema."""
        tool = TOOL_SCHEMAS["call_restlet"]
        props = tool.input_schema["properties"]
        assert "url" in props
        assert "method" in props
        assert props["method"]["enum"] == ["GET", "POST", "PUT", "DELETE"]
    
    def test_list_records_schema(self):
        """Test list_records tool schema."""
        tool = TOOL_SCHEMAS["list_records"]
        props = tool.input_schema["properties"]
        assert "record_type" in props
        assert "limit" in props
        assert "offset" in props
    
    def test_run_saved_search_schema(self):
        """Test run_saved_search tool schema."""
        tool = TOOL_SCHEMAS["run_saved_search"]
        assert "search_id" in tool.input_schema["properties"]


class TestGetToolDefinitions:
    """Tests for get_tool_definitions function."""
    
    def test_returns_list(self):
        """Test get_tool_definitions returns a list."""
        tools = get_tool_definitions()
        assert isinstance(tools, list)
    
    def test_returns_correct_format(self):
        """Test each tool has correct MCP format."""
        tools = get_tool_definitions()
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    def test_returns_all_tools(self):
        """Test all defined tools are returned."""
        tools = get_tool_definitions()
        tool_names = [t["name"] for t in tools]
        for name in TOOL_SCHEMAS.keys():
            assert name in tool_names


class TestMCPToolHandler:
    """Tests for MCPToolHandler class."""
    
    def test_handler_initialization(self, tool_handler):
        """Test tool handler initializes correctly."""
        assert tool_handler.netsuite is not None
        assert tool_handler.odbc is not None
        assert "123456-sb1" in tool_handler._account_base_url
    
    def test_format_response_success(self, tool_handler):
        """Test _format_response with successful response."""
        result = NetsuiteObject(
            response=json.dumps({"id": "123"}),
            code=200
        )
        formatted = tool_handler._format_response(result)
        
        assert "content" in formatted
        assert formatted["isError"] is False
        content_text = json.loads(formatted["content"][0]["text"])
        assert content_text["status_code"] == 200
    
    def test_format_response_error(self, tool_handler):
        """Test _format_response with error response."""
        result = NetsuiteObject(
            response=json.dumps({"error": "Not found"}),
            code=404
        )
        formatted = tool_handler._format_response(result)
        
        assert formatted["isError"] is True
        content_text = json.loads(formatted["content"][0]["text"])
        assert content_text["status_code"] == 404
    
    def test_format_response_invalid_json(self, tool_handler):
        """Test _format_response handles invalid JSON."""
        result = NetsuiteObject(
            response="Not valid JSON",
            code=200
        )
        formatted = tool_handler._format_response(result)
        
        content_text = json.loads(formatted["content"][0]["text"])
        assert content_text["data"] == "Not valid JSON"
    
    def test_format_error(self, tool_handler):
        """Test _format_error creates error response."""
        formatted = tool_handler._format_error("Test error message")
        
        assert formatted["isError"] is True
        content_text = json.loads(formatted["content"][0]["text"])
        assert content_text["error"] == "Test error message"
    
    def test_handle_query_missing_param(self, tool_handler):
        """Test handle_query_netsuite with missing query."""
        result = tool_handler.handle_query_netsuite({})
        assert result["isError"] is True
    
    def test_handle_get_record_missing_params(self, tool_handler):
        """Test handle_get_record with missing parameters."""
        result = tool_handler.handle_get_record({})
        assert result["isError"] is True
        
        result = tool_handler.handle_get_record({"record_type": "customer"})
        assert result["isError"] is True
    
    def test_handle_create_record_missing_params(self, tool_handler):
        """Test handle_create_record with missing parameters."""
        result = tool_handler.handle_create_record({})
        assert result["isError"] is True
    
    def test_handle_update_record_missing_params(self, tool_handler):
        """Test handle_update_record with missing parameters."""
        result = tool_handler.handle_update_record({})
        assert result["isError"] is True
        
        result = tool_handler.handle_update_record({
            "record_type": "customer",
            "record_id": "123"
        })
        assert result["isError"] is True
    
    def test_handle_delete_record_missing_params(self, tool_handler):
        """Test handle_delete_record with missing parameters."""
        result = tool_handler.handle_delete_record({})
        assert result["isError"] is True
    
    def test_handle_call_restlet_missing_url(self, tool_handler):
        """Test handle_call_restlet with missing URL."""
        result = tool_handler.handle_call_restlet({"method": "GET"})
        assert result["isError"] is True
    
    def test_handle_call_restlet_invalid_method(self, tool_handler):
        """Test handle_call_restlet with invalid HTTP method."""
        result = tool_handler.handle_call_restlet({
            "url": "https://test.com",
            "method": "INVALID"
        })
        assert result["isError"] is True
    
    def test_handle_list_records_missing_type(self, tool_handler):
        """Test handle_list_records with missing record_type."""
        result = tool_handler.handle_list_records({})
        assert result["isError"] is True
    
    def test_handle_run_saved_search_missing_id(self, tool_handler):
        """Test handle_run_saved_search with missing search_id."""
        result = tool_handler.handle_run_saved_search({})
        assert result["isError"] is True
    
    def test_call_tool_unknown(self, tool_handler):
        """Test call_tool with unknown tool name."""
        result = tool_handler.call_tool("unknown_tool", {})
        assert result["isError"] is True
        content = json.loads(result["content"][0]["text"])
        assert "Unknown tool" in content["error"]
    
    def test_call_tool_routes_correctly(self, tool_handler):
        """Test call_tool routes to correct handler."""
        with patch.object(tool_handler, 'handle_query_netsuite') as mock:
            mock.return_value = {"content": [], "isError": False}
            tool_handler.call_tool("query_netsuite", {"query": "SELECT 1"})
            mock.assert_called_once_with({"query": "SELECT 1"})
