"""
Tests for run_stdio_server function.
"""
import json
import pytest
import sys
sys.path.insert(0, "/home/runner/workspace/src")

from unittest.mock import patch, MagicMock
from io import StringIO

from NetSuite_Connector.mcp_server import run_stdio_server, NetSuiteMCPServer


class TestRunStdioServer:
    """Tests for run_stdio_server function."""
    
    def test_server_with_direct_credentials(self, monkeypatch):
        """Test running server with direct credentials."""
        stdin_data = '{"jsonrpc": "2.0", "id": 1, "method": "ping"}\n'
        mock_stdin = StringIO(stdin_data)
        mock_stdout = StringIO()
        
        monkeypatch.setattr('sys.stdin', mock_stdin)
        monkeypatch.setattr('sys.stdout', mock_stdout)
        
        run_stdio_server(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        output = mock_stdout.getvalue()
        assert '"pong": true' in output
    
    def test_server_from_env(self, monkeypatch):
        """Test running server from environment variables."""
        monkeypatch.setenv("NETSUITE_ACCOUNT_ID", "env_test")
        monkeypatch.setenv("NETSUITE_CONSUMER_KEY", "ck")
        monkeypatch.setenv("NETSUITE_CONSUMER_SECRET", "cs")
        monkeypatch.setenv("NETSUITE_TOKEN_KEY", "tk")
        monkeypatch.setenv("NETSUITE_TOKEN_SECRET", "ts")
        
        stdin_data = '{"jsonrpc": "2.0", "id": 1, "method": "initialize"}\n'
        mock_stdin = StringIO(stdin_data)
        mock_stdout = StringIO()
        
        monkeypatch.setattr('sys.stdin', mock_stdin)
        monkeypatch.setattr('sys.stdout', mock_stdout)
        
        run_stdio_server()
        
        output = mock_stdout.getvalue()
        response = json.loads(output.strip())
        assert response["result"]["serverInfo"]["name"] == "netsuite-connector-mcp"
    
    def test_server_handles_multiple_requests(self, monkeypatch):
        """Test server handles multiple sequential requests."""
        stdin_data = (
            '{"jsonrpc": "2.0", "id": 1, "method": "initialize"}\n'
            '{"jsonrpc": "2.0", "id": 2, "method": "ping"}\n'
            '{"jsonrpc": "2.0", "id": 3, "method": "tools/list"}\n'
        )
        mock_stdin = StringIO(stdin_data)
        mock_stdout = StringIO()
        
        monkeypatch.setattr('sys.stdin', mock_stdin)
        monkeypatch.setattr('sys.stdout', mock_stdout)
        
        run_stdio_server(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        output_lines = mock_stdout.getvalue().strip().split('\n')
        assert len(output_lines) == 3
        
        for line in output_lines:
            response = json.loads(line)
            assert "result" in response
    
    def test_server_handles_json_parse_error(self, monkeypatch):
        """Test server handles invalid JSON."""
        stdin_data = 'not valid json\n{"jsonrpc": "2.0", "id": 1, "method": "ping"}\n'
        mock_stdin = StringIO(stdin_data)
        mock_stdout = StringIO()
        
        monkeypatch.setattr('sys.stdin', mock_stdin)
        monkeypatch.setattr('sys.stdout', mock_stdout)
        
        run_stdio_server(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        output_lines = mock_stdout.getvalue().strip().split('\n')
        assert len(output_lines) == 2
        
        error_response = json.loads(output_lines[0])
        assert "error" in error_response
        assert error_response["error"]["code"] == -32700
        
        success_response = json.loads(output_lines[1])
        assert "result" in success_response
    
    def test_server_handles_empty_lines(self, monkeypatch):
        """Test server handles empty lines gracefully."""
        stdin_data = '\n\n{"jsonrpc": "2.0", "id": 1, "method": "ping"}\n\n'
        mock_stdin = StringIO(stdin_data)
        mock_stdout = StringIO()
        
        monkeypatch.setattr('sys.stdin', mock_stdin)
        monkeypatch.setattr('sys.stdout', mock_stdout)
        
        run_stdio_server(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        output = mock_stdout.getvalue().strip()
        response = json.loads(output)
        assert response["result"]["pong"] is True
    
    def test_server_logs_to_stderr(self, monkeypatch, capsys):
        """Test server logs startup info to stderr."""
        stdin_data = '{"jsonrpc": "2.0", "id": 1, "method": "ping"}\n'
        mock_stdin = StringIO(stdin_data)
        mock_stdout = StringIO()
        
        monkeypatch.setattr('sys.stdin', mock_stdin)
        monkeypatch.setattr('sys.stdout', mock_stdout)
        
        run_stdio_server(
            account_id="123456",
            consumer_keys={"consumer_key": "ck", "consumer_secret": "cs"},
            token_keys={"token_key": "tk", "token_secret": "ts"}
        )
        
        captured = capsys.readouterr()
        assert "NetSuite MCP Server started" in captured.err
        assert "stdio mode" in captured.err
