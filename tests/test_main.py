"""
Tests for __main__ module (CLI entry point).
"""
import pytest
import sys
sys.path.insert(0, "/home/runner/workspace/src")

from unittest.mock import patch, MagicMock
from io import StringIO

from NetSuite_Connector.__main__ import main
from NetSuite_Connector.mcp_config import ConfigurationError


class TestMainCLI:
    """Tests for CLI entry point."""
    
    def test_version_flag(self):
        """Test --version flag shows version."""
        with patch('sys.argv', ['netsuite-mcp', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
    
    def test_check_config_success(self, monkeypatch):
        """Test --check-config with valid config."""
        monkeypatch.setenv("NETSUITE_ACCOUNT_ID", "test_account")
        monkeypatch.setenv("NETSUITE_CONSUMER_KEY", "test_ck_12345678")
        monkeypatch.setenv("NETSUITE_CONSUMER_SECRET", "test_cs")
        monkeypatch.setenv("NETSUITE_TOKEN_KEY", "test_tk_12345678")
        monkeypatch.setenv("NETSUITE_TOKEN_SECRET", "test_ts")
        
        with patch('sys.argv', ['netsuite-mcp', '--check-config']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
    
    def test_check_config_failure(self, monkeypatch):
        """Test --check-config with missing config."""
        monkeypatch.delenv("NETSUITE_ACCOUNT_ID", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_SECRET", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_SECRET", raising=False)
        
        with patch('sys.argv', ['netsuite-mcp', '--check-config']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    def test_list_tools_success(self, monkeypatch):
        """Test --list-tools with valid config."""
        monkeypatch.setenv("NETSUITE_ACCOUNT_ID", "test_account")
        monkeypatch.setenv("NETSUITE_CONSUMER_KEY", "test_ck")
        monkeypatch.setenv("NETSUITE_CONSUMER_SECRET", "test_cs")
        monkeypatch.setenv("NETSUITE_TOKEN_KEY", "test_tk")
        monkeypatch.setenv("NETSUITE_TOKEN_SECRET", "test_ts")
        
        with patch('sys.argv', ['netsuite-mcp', '--list-tools']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
    
    def test_list_tools_failure(self, monkeypatch):
        """Test --list-tools with missing config."""
        monkeypatch.delenv("NETSUITE_ACCOUNT_ID", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_SECRET", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_SECRET", raising=False)
        
        with patch('sys.argv', ['netsuite-mcp', '--list-tools']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    def test_run_server_config_error(self, monkeypatch):
        """Test running server with missing config."""
        monkeypatch.delenv("NETSUITE_ACCOUNT_ID", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_SECRET", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_SECRET", raising=False)
        
        with patch('sys.argv', ['netsuite-mcp']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    def test_run_server_keyboard_interrupt(self, monkeypatch):
        """Test running server handles keyboard interrupt."""
        monkeypatch.setenv("NETSUITE_ACCOUNT_ID", "test")
        monkeypatch.setenv("NETSUITE_CONSUMER_KEY", "ck")
        monkeypatch.setenv("NETSUITE_CONSUMER_SECRET", "cs")
        monkeypatch.setenv("NETSUITE_TOKEN_KEY", "tk")
        monkeypatch.setenv("NETSUITE_TOKEN_SECRET", "ts")
        
        with patch('sys.argv', ['netsuite-mcp']):
            with patch('NetSuite_Connector.__main__.run_stdio_server') as mock:
                mock.side_effect = KeyboardInterrupt()
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
