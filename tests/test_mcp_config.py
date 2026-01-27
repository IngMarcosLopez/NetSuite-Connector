"""
Tests for MCP Configuration module.
"""
import os
import pytest
import sys
sys.path.insert(0, "/home/runner/workspace/src")

from NetSuite_Connector.mcp_config import (
    NetSuiteConfig,
    ConfigurationError,
    load_config_from_env,
    validate_config
)


class TestNetSuiteConfig:
    """Tests for NetSuiteConfig dataclass."""
    
    def test_config_creation(self):
        """Test creating a config object with all fields."""
        config = NetSuiteConfig(
            account_id="123456_SB1",
            consumer_key="ck_test",
            consumer_secret="cs_test",
            token_key="tk_test",
            token_secret="ts_test"
        )
        assert config.account_id == "123456_SB1"
        assert config.consumer_key == "ck_test"
        assert config.consumer_secret == "cs_test"
        assert config.token_key == "tk_test"
        assert config.token_secret == "ts_test"
    
    def test_consumer_keys_property(self):
        """Test consumer_keys property returns correct dict."""
        config = NetSuiteConfig(
            account_id="123456",
            consumer_key="ck",
            consumer_secret="cs",
            token_key="tk",
            token_secret="ts"
        )
        keys = config.consumer_keys
        assert keys == {"consumer_key": "ck", "consumer_secret": "cs"}
    
    def test_token_keys_property(self):
        """Test token_keys property returns correct dict."""
        config = NetSuiteConfig(
            account_id="123456",
            consumer_key="ck",
            consumer_secret="cs",
            token_key="tk",
            token_secret="ts"
        )
        keys = config.token_keys
        assert keys == {"token_key": "tk", "token_secret": "ts"}


class TestLoadConfigFromEnv:
    """Tests for load_config_from_env function."""
    
    def test_load_from_env_vars(self, monkeypatch):
        """Test loading config from environment variables."""
        monkeypatch.setenv("NETSUITE_ACCOUNT_ID", "env_account")
        monkeypatch.setenv("NETSUITE_CONSUMER_KEY", "env_ck")
        monkeypatch.setenv("NETSUITE_CONSUMER_SECRET", "env_cs")
        monkeypatch.setenv("NETSUITE_TOKEN_KEY", "env_tk")
        monkeypatch.setenv("NETSUITE_TOKEN_SECRET", "env_ts")
        
        config = load_config_from_env()
        
        assert config.account_id == "env_account"
        assert config.consumer_key == "env_ck"
        assert config.consumer_secret == "env_cs"
        assert config.token_key == "env_tk"
        assert config.token_secret == "env_ts"
    
    def test_direct_params_override_env(self, monkeypatch):
        """Test that direct parameters override environment variables."""
        monkeypatch.setenv("NETSUITE_ACCOUNT_ID", "env_account")
        monkeypatch.setenv("NETSUITE_CONSUMER_KEY", "env_ck")
        monkeypatch.setenv("NETSUITE_CONSUMER_SECRET", "env_cs")
        monkeypatch.setenv("NETSUITE_TOKEN_KEY", "env_tk")
        monkeypatch.setenv("NETSUITE_TOKEN_SECRET", "env_ts")
        
        config = load_config_from_env(
            account_id="override_account",
            consumer_key="override_ck"
        )
        
        assert config.account_id == "override_account"
        assert config.consumer_key == "override_ck"
        assert config.consumer_secret == "env_cs"
    
    def test_missing_env_vars_raises_error(self, monkeypatch):
        """Test that missing environment variables raise ConfigurationError."""
        monkeypatch.delenv("NETSUITE_ACCOUNT_ID", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_SECRET", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_SECRET", raising=False)
        
        with pytest.raises(ConfigurationError) as exc_info:
            load_config_from_env()
        
        assert "Missing required configuration" in str(exc_info.value)
    
    def test_partial_missing_env_vars(self, monkeypatch):
        """Test error when only some env vars are missing."""
        monkeypatch.setenv("NETSUITE_ACCOUNT_ID", "account")
        monkeypatch.setenv("NETSUITE_CONSUMER_KEY", "ck")
        monkeypatch.delenv("NETSUITE_CONSUMER_SECRET", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_SECRET", raising=False)
        
        with pytest.raises(ConfigurationError) as exc_info:
            load_config_from_env()
        
        error_msg = str(exc_info.value)
        assert "consumer_secret" in error_msg
        assert "token_key" in error_msg
        assert "token_secret" in error_msg
    
    def test_no_raise_on_missing(self, monkeypatch):
        """Test raise_on_missing=False returns empty strings."""
        monkeypatch.delenv("NETSUITE_ACCOUNT_ID", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_CONSUMER_SECRET", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_KEY", raising=False)
        monkeypatch.delenv("NETSUITE_TOKEN_SECRET", raising=False)
        
        config = load_config_from_env(raise_on_missing=False)
        
        assert config.account_id == ""
        assert config.consumer_key == ""


class TestValidateConfig:
    """Tests for validate_config function."""
    
    def test_valid_config_no_errors(self, sample_config):
        """Test that valid config returns empty error list."""
        errors = validate_config(sample_config)
        assert errors == []
    
    def test_empty_account_id(self):
        """Test validation catches empty account_id."""
        config = NetSuiteConfig(
            account_id="",
            consumer_key="ck",
            consumer_secret="cs",
            token_key="tk",
            token_secret="ts"
        )
        errors = validate_config(config)
        assert "account_id is required" in errors
    
    def test_empty_consumer_key(self):
        """Test validation catches empty consumer_key."""
        config = NetSuiteConfig(
            account_id="123",
            consumer_key="",
            consumer_secret="cs",
            token_key="tk",
            token_secret="ts"
        )
        errors = validate_config(config)
        assert "consumer_key is required" in errors
    
    def test_empty_consumer_secret(self):
        """Test validation catches empty consumer_secret."""
        config = NetSuiteConfig(
            account_id="123",
            consumer_key="ck",
            consumer_secret="",
            token_key="tk",
            token_secret="ts"
        )
        errors = validate_config(config)
        assert "consumer_secret is required" in errors
    
    def test_empty_token_key(self):
        """Test validation catches empty token_key."""
        config = NetSuiteConfig(
            account_id="123",
            consumer_key="ck",
            consumer_secret="cs",
            token_key="",
            token_secret="ts"
        )
        errors = validate_config(config)
        assert "token_key is required" in errors
    
    def test_empty_token_secret(self):
        """Test validation catches empty token_secret."""
        config = NetSuiteConfig(
            account_id="123",
            consumer_key="ck",
            consumer_secret="cs",
            token_key="tk",
            token_secret=""
        )
        errors = validate_config(config)
        assert "token_secret is required" in errors
    
    def test_multiple_empty_fields(self):
        """Test validation catches multiple empty fields."""
        config = NetSuiteConfig(
            account_id="",
            consumer_key="",
            consumer_secret="cs",
            token_key="",
            token_secret="ts"
        )
        errors = validate_config(config)
        assert len(errors) == 3
        assert "account_id is required" in errors
        assert "consumer_key is required" in errors
        assert "token_key is required" in errors
