"""
Tests for MCP Server module.
"""
import json
import pytest
import sys
sys.path.insert(0, "/home/runner/workspace/src")

from unittest.mock import Mock, patch

from NetSuite_Connector.mcp_server import NetSuiteMCPServer, run_stdio_server
from NetSuite_Connector.mcp_config import NetSuiteConfig


class TestNetSuiteMCPServer:
    """Tests for NetSuiteMCPServer class."""
    
    def test_server_initialization(self, mcp_server):
        """Test server initializes with correct components."""
        assert mcp_server.netsuite is not None
        assert mcp_server.odbc is not None
        assert mcp_server.tool_handler is not None
    
    def test_server_version(self, mcp_server):
        """Test server has version defined."""
        assert mcp_server.VERSION == "0.1.0"
        assert mcp_server.PROTOCOL_VERSION == "2024-11-05"
    
    def test_from_config_classmethod(self, sample_config):
        """Test creating server from config object."""
        server = NetSuiteMCPServer.from_config(sample_config)
        assert server.netsuite.account_id == sample_config.account_id
    
    def test_from_env_classmethod(self, monkeypatch):
        """Test creating server from environment variables."""
        monkeypatch.setenv("NETSUITE_ACCOUNT_ID", "env_test")
        monkeypatch.setenv("NETSUITE_CONSUMER_KEY", "ck")
        monkeypatch.setenv("NETSUITE_CONSUMER_SECRET", "cs")
        monkeypatch.setenv("NETSUITE_TOKEN_KEY", "tk")
        monkeypatch.setenv("NETSUITE_TOKEN_SECRET", "ts")
        
        server = NetSuiteMCPServer.from_env()
        assert server.netsuite.account_id == "env_test"
    
    def test_list_tools(self, mcp_server):
        """Test list_tools returns all available tools."""
        tools = mcp_server.list_tools()
        assert isinstance(tools, list)
        assert len(tools) == 8
        
        tool_names = [t["name"] for t in tools]
        assert "query_netsuite" in tool_names
        assert "get_record" in tool_names
        assert "create_record" in tool_names
    
    def test_list_tools_format(self, mcp_server):
        """Test list_tools returns correct MCP format."""
        tools = mcp_server.list_tools()
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    def test_call_tool_delegates_to_handler(self, mcp_server):
        """Test call_tool delegates to tool_handler."""
        with patch.object(mcp_server.tool_handler, 'call_tool') as mock:
            mock.return_value = {"content": [], "isError": False}
            mcp_server.call_tool("query_netsuite", {"query": "SELECT 1"})
            mock.assert_called_once()


class TestMCPProtocolHandling:
    """Tests for MCP protocol request handling."""
    
    def test_handle_initialize(self, mcp_server):
        """Test handling initialize request."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize"
        }
        response = mcp_server.handle_mcp_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert response["result"]["serverInfo"]["name"] == "netsuite-connector-mcp"
    
    def test_handle_notifications_initialized(self, mcp_server):
        """Test handling notifications/initialized request."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "notifications/initialized"
        }
        response = mcp_server.handle_mcp_request(request)
        
        assert response["id"] == 2
        assert response["result"] == {}
    
    def test_handle_tools_list(self, mcp_server):
        """Test handling tools/list request."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list"
        }
        response = mcp_server.handle_mcp_request(request)
        
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) == 8
    
    def test_handle_tools_call(self, mcp_server):
        """Test handling tools/call request."""
        with patch.object(mcp_server.tool_handler, 'call_tool') as mock:
            mock.return_value = {"content": [{"type": "text", "text": "{}"}], "isError": False}
            
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "query_netsuite",
                    "arguments": {"query": "SELECT 1"}
                }
            }
            response = mcp_server.handle_mcp_request(request)
            
            assert "result" in response
            mock.assert_called_once_with("query_netsuite", {"query": "SELECT 1"})
    
    def test_handle_ping(self, mcp_server):
        """Test handling ping request."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "ping"
        }
        response = mcp_server.handle_mcp_request(request)
        
        assert response["result"]["pong"] is True
    
    def test_handle_unknown_method(self, mcp_server):
        """Test handling unknown method request."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "unknown/method"
        }
        response = mcp_server.handle_mcp_request(request)
        
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]
    
    def test_handle_request_preserves_id(self, mcp_server):
        """Test that request ID is preserved in response."""
        request = {
            "jsonrpc": "2.0",
            "id": "custom-id-123",
            "method": "ping"
        }
        response = mcp_server.handle_mcp_request(request)
        
        assert response["id"] == "custom-id-123"
    
    def test_handle_request_with_null_id(self, mcp_server):
        """Test handling request with null ID (notification)."""
        request = {
            "jsonrpc": "2.0",
            "id": None,
            "method": "ping"
        }
        response = mcp_server.handle_mcp_request(request)
        
        assert response["id"] is None
    
    def test_handle_request_exception(self, mcp_server):
        """Test handling when tool raises exception."""
        with patch.object(mcp_server.tool_handler, 'call_tool') as mock:
            mock.side_effect = Exception("Unexpected error")
            
            request = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {"name": "query_netsuite", "arguments": {}}
            }
            response = mcp_server.handle_mcp_request(request)
            
            assert "error" in response
            assert response["error"]["code"] == -32603
            assert "Internal error" in response["error"]["message"]


class TestMCPServerIntegration:
    """Integration tests for MCP Server."""
    
    def test_full_mcp_flow(self, mcp_server):
        """Test complete MCP protocol flow."""
        init_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
        init_response = mcp_server.handle_mcp_request(init_request)
        assert "result" in init_response
        
        initialized_request = {"jsonrpc": "2.0", "id": 2, "method": "notifications/initialized"}
        initialized_response = mcp_server.handle_mcp_request(initialized_request)
        assert initialized_response["result"] == {}
        
        list_request = {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}
        list_response = mcp_server.handle_mcp_request(list_request)
        assert len(list_response["result"]["tools"]) > 0
    
    def test_tool_call_returns_mcp_format(self, mcp_server):
        """Test tool call returns proper MCP response format."""
        result = mcp_server.call_tool("query_netsuite", {})
        
        assert "content" in result or "isError" in result
