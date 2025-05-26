#!/bin/bash
# YouTrack FastMCP Wrapper Script for Claude MCP integration
# This script starts the YouTrack MCP server using Docker

# Load environment variables from .env file if it exists
if [ -f "$(dirname "$0")/../.env" ]; then
    export $(grep -v '^#' "$(dirname "$0")/../.env" | xargs)
fi

# Start the YouTrack MCP server
docker run --rm -i \
  --env-file "$(dirname "$0")/../.env" \
  youtrack-mcp-fastmcp:latest