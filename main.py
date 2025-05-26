#!/usr/bin/env python3
"""
YouTrack MCP Server - FastMCP 2.0 implementation.
"""
import argparse
import logging
import os
import signal
import sys

from youtrack_mcp.config import Config, config
from youtrack_mcp.fastmcp_server import get_server, close

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from environment variables or file."""
    env_config = {}
    
    # Extract config variables from environment
    for key in dir(Config):
        if key.isupper() and not key.startswith("_"):
            env_key = f"YOUTRACK_MCP_{key}"
            if env_key in os.environ:
                env_value = os.environ[env_key]
                # Convert string booleans to actual booleans
                if env_value.lower() in ("true", "false"):
                    env_value = env_value.lower() == "true"
                env_config[key] = env_value
    
    # Create config instance from environment variables
    if env_config:
        logger.info("Loading configuration from environment variables")
        Config.from_dict(env_config)
    
    # Log configuration status
    if config.YOUTRACK_URL:
        logger.info(f"Configured for self-hosted YouTrack instance at: {config.YOUTRACK_URL}")
    else:
        logger.info("Configured for YouTrack Cloud instance")
    
    logger.info(f"SSL verification: {'Enabled' if config.VERIFY_SSL else 'Disabled'}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="YouTrack MCP Server (FastMCP 2.0)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument(
        "--log-level", 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    parser.add_argument(
        "--youtrack-url", 
        help="YouTrack instance URL (not required for YouTrack Cloud)"
    )
    parser.add_argument(
        "--api-token", 
        help="YouTrack API token for authentication"
    )
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        default=None,
        help="Verify SSL certificates (default: True)"
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_false",
        dest="verify_ssl",
        help="Disable SSL certificate verification"
    )
    
    return parser.parse_args()


def apply_cli_args(args):
    """Apply command line arguments to configuration."""
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Apply YouTrack configuration
    config_dict = {}
    
    if args.youtrack_url:
        config_dict["YOUTRACK_URL"] = args.youtrack_url
    
    if args.api_token:
        config_dict["YOUTRACK_API_TOKEN"] = args.api_token
    
    if args.verify_ssl is not None:
        config_dict["VERIFY_SSL"] = args.verify_ssl
    
    if config_dict:
        Config.from_dict(config_dict)


def handle_signal(signum: int, frame) -> None:
    """
    Handle termination signals.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logging.info(f"Received signal {signum}, shutting down...")
    close()
    sys.exit(0)


def main():
    """Run the FastMCP 2.0 server."""
    args = parse_args()
    
    # Apply command line arguments
    apply_cli_args(args)
    
    # Load configuration
    load_config()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        # Get FastMCP server
        server = get_server()
        
        logger.info(f"Starting YouTrack MCP server ({config.MCP_SERVER_NAME}) on {args.host}:{args.port}")
        
        # Run the server (FastMCP handles HTTP automatically)
        server.run()
        
    except Exception as e:
        logging.exception(f"Error starting server: {e}")
        sys.exit(1)
    finally:
        close()


if __name__ == "__main__":
    main()