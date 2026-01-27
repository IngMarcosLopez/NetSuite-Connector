"""
MCP Configuration Module
Loads NetSuite credentials from environment variables or direct parameters.
"""
import os
from dataclasses import dataclass
from typing import Optional


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


@dataclass
class NetSuiteConfig:
    """Configuration for NetSuite MCP Server."""
    account_id: str
    consumer_key: str
    consumer_secret: str
    token_key: str
    token_secret: str
    
    @property
    def consumer_keys(self) -> dict:
        return {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret
        }
    
    @property
    def token_keys(self) -> dict:
        return {
            "token_key": self.token_key,
            "token_secret": self.token_secret
        }


def load_config_from_env(
    account_id: Optional[str] = None,
    consumer_key: Optional[str] = None,
    consumer_secret: Optional[str] = None,
    token_key: Optional[str] = None,
    token_secret: Optional[str] = None,
    raise_on_missing: bool = True
) -> NetSuiteConfig:
    """
    Load NetSuite configuration from environment variables.
    Direct parameters override environment variables.
    
    Environment variables:
        - NETSUITE_ACCOUNT_ID
        - NETSUITE_CONSUMER_KEY
        - NETSUITE_CONSUMER_SECRET
        - NETSUITE_TOKEN_KEY
        - NETSUITE_TOKEN_SECRET
    
    Args:
        account_id: Override for account ID
        consumer_key: Override for consumer key
        consumer_secret: Override for consumer secret
        token_key: Override for token key
        token_secret: Override for token secret
        raise_on_missing: If True, raises ConfigurationError for missing values
    
    Returns:
        NetSuiteConfig with loaded values
    
    Raises:
        ConfigurationError: If required values are missing and raise_on_missing is True
    """
    config_values = {
        "account_id": account_id or os.environ.get("NETSUITE_ACCOUNT_ID"),
        "consumer_key": consumer_key or os.environ.get("NETSUITE_CONSUMER_KEY"),
        "consumer_secret": consumer_secret or os.environ.get("NETSUITE_CONSUMER_SECRET"),
        "token_key": token_key or os.environ.get("NETSUITE_TOKEN_KEY"),
        "token_secret": token_secret or os.environ.get("NETSUITE_TOKEN_SECRET"),
    }
    
    if raise_on_missing:
        missing = [k for k, v in config_values.items() if not v]
        if missing:
            env_vars = [f"NETSUITE_{k.upper()}" for k in missing]
            raise ConfigurationError(
                f"Missing required configuration: {missing}. "
                f"Set environment variables: {env_vars}"
            )
    
    return NetSuiteConfig(
        account_id=config_values["account_id"] or "",
        consumer_key=config_values["consumer_key"] or "",
        consumer_secret=config_values["consumer_secret"] or "",
        token_key=config_values["token_key"] or "",
        token_secret=config_values["token_secret"] or "",
    )


def validate_config(config: NetSuiteConfig) -> list[str]:
    """
    Validate configuration values.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not config.account_id:
        errors.append("account_id is required")
    
    if not config.consumer_key:
        errors.append("consumer_key is required")
    
    if not config.consumer_secret:
        errors.append("consumer_secret is required")
    
    if not config.token_key:
        errors.append("token_key is required")
    
    if not config.token_secret:
        errors.append("token_secret is required")
    
    return errors
