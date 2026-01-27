"""
Entry point for running the NetSuite MCP Server.

Usage:
    python -m NetSuite_Connector.mcp_server

Environment Variables:
    NETSUITE_ACCOUNT_ID     - NetSuite account ID (e.g., 123456_SB1)
    NETSUITE_CONSUMER_KEY   - OAuth consumer key
    NETSUITE_CONSUMER_SECRET - OAuth consumer secret
    NETSUITE_TOKEN_KEY      - Token-based auth token key
    NETSUITE_TOKEN_SECRET   - Token-based auth token secret
"""
import argparse
import sys

from .mcp_config import ConfigurationError, load_config_from_env
from .mcp_server import NetSuiteMCPServer, run_stdio_server


def main():
    parser = argparse.ArgumentParser(
        description="NetSuite MCP Server - Connect AI assistants to NetSuite"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"NetSuite MCP Server {NetSuiteMCPServer.VERSION}"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available MCP tools and exit"
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check configuration and exit"
    )
    
    args = parser.parse_args()
    
    if args.check_config:
        try:
            config = load_config_from_env()
            print("Configuration OK")
            print(f"  Account ID: {config.account_id}")
            print(f"  Consumer Key: {config.consumer_key[:8]}...")
            print(f"  Token Key: {config.token_key[:8]}...")
            sys.exit(0)
        except ConfigurationError as e:
            print(f"Configuration Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    if args.list_tools:
        try:
            config = load_config_from_env()
            server = NetSuiteMCPServer.from_config(config)
            tools = server.list_tools()
            print(f"Available MCP Tools ({len(tools)}):")
            print("-" * 50)
            for tool in tools:
                print(f"\n{tool['name']}")
                print(f"  {tool['description']}")
                required = tool.get('inputSchema', {}).get('required', [])
                if required:
                    print(f"  Required: {', '.join(required)}")
            sys.exit(0)
        except ConfigurationError as e:
            print(f"Configuration Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    try:
        run_stdio_server()
    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        print("\nSet the following environment variables:", file=sys.stderr)
        print("  NETSUITE_ACCOUNT_ID", file=sys.stderr)
        print("  NETSUITE_CONSUMER_KEY", file=sys.stderr)
        print("  NETSUITE_CONSUMER_SECRET", file=sys.stderr)
        print("  NETSUITE_TOKEN_KEY", file=sys.stderr)
        print("  NETSUITE_TOKEN_SECRET", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
