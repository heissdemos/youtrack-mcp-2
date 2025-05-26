# YouTrack MCP Server (FastMCP 2.0)

A modern Model Context Protocol (MCP) server implementation for JetBrains YouTrack, built with FastMCP 2.0. This server allows AI assistants to interact with YouTrack issue tracking systems through a clean, decorator-based architecture.

![Screenshot](screenshot/CleanShot%202025-04-14%20at%2023.24.21@2x.png)

## What is MCP?

Model Context Protocol (MCP) is an open standard that enables AI models to interact with external tools and services through a unified interface. This project provides an MCP server that exposes YouTrack functionality to AI assistants that support the MCP standard, such as Claude.

## Features

- **Issue Management**
  - Get issue details
  - Search for issues using YouTrack query language
  - Create new issues
  - Add comments to issues

- **Project Management**
  - Get project list and details
  - Create and update projects
  - Access project issues

- **User Management**
  - Get current user information
  - Search for users
  - Access user details

- **Time Tracking**
  - Record work time on issues
  - Retrieve time tracking entries
  - Update and delete time records
  - Support for time in various formats (e.g., "2h 30m")

- **Search Functionality**
  - Advanced search with custom fields
  - Structured filtering
  - Sorting options

## Installation & Usage

### Using Docker (Recommended)

1. Pull the Docker image:
   ```bash
   docker pull youtrack-mcp-fastmcp:latest
   ```

2. Run the container with your YouTrack credentials:
   ```bash
   docker run -i --rm \
     -e YOUTRACK_URL=https://your-instance.youtrack.cloud \
     -e YOUTRACK_API_TOKEN=your-api-token \
     youtrack-mcp-fastmcp:latest
   ```

   Note: The `-i` flag is important as it keeps STDIN open, which is required for the MCP stdio transport.

### Building from Source

1. Clone the repository:
   ```bash
   git clone <this-repo>
   cd youtrack-mcp-2
   ```

2. Build the Docker image:
   ```bash
   docker build -t youtrack-mcp-fastmcp:latest .
   ```

## Using with Claude

To connect this MCP server with Claude, use the `claude mcp add` command:

```bash
claude mcp add \
  -e YOUTRACK_URL=https://your-instance.youtrack.cloud \
  -e YOUTRACK_API_TOKEN=your-api-token \
  youtrack-fastmcp \
  docker run --rm -i youtrack-mcp-fastmcp:latest
```

Alternatively, create a wrapper script and add it:

```bash
# Create wrapper script
cat > youtrack-mcp-wrapper.sh << 'EOF'
#!/bin/bash
docker run --rm -i \
  -e YOUTRACK_URL=https://your-instance.youtrack.cloud \
  -e YOUTRACK_API_TOKEN=your-api-token \
  youtrack-mcp-fastmcp:latest
EOF
chmod +x youtrack-mcp-wrapper.sh

# Add to Claude
claude mcp add youtrack-fastmcp ./youtrack-mcp-wrapper.sh
```

## Available Tools

The YouTrack MCP server provides the following tools via FastMCP decorators:

### Issues

- `get_issue` - Get details of a specific issue by ID
- `search_issues` - Search for issues using YouTrack query language
- `create_issue` - Create a new issue in a specific project
- `add_comment` - Add a comment to an existing issue

### Projects

- `get_projects` - Get a list of all projects
- `get_project` - Get details of a specific project
- `get_project_issues` - Get issues for a specific project
- `create_project` - Create a new project

### Users

- `get_current_user` - Get information about the currently authenticated user
- `get_user` - Get information about a specific user
- `search_users` - Search for users

### Time Tracking

- `get_work_items` - Get work items (time tracking entries) for a specific issue
- `create_work_item` - Create a new work item for an issue (record time spent)
- `update_work_item` - Update an existing work item
- `delete_work_item` - Delete a work item

Time tracking is protected by validation mechanisms:
1. **Allowed Tickets**: Only tickets in the allowed list can receive time entries (configurable via parent-ticket.json)
2. **Closed Ticket Protection**: Time cannot be booked on resolved/closed tickets

### Search

- `advanced_search` - Advanced search with sorting options
- `filter_issues` - Search with structured filtering
- `search_with_custom_fields` - Search using custom field values

## Examples

Here are some examples of using the YouTrack MCP server with AI assistants:

### Get Issue
```
Can you get the details for issue DEMO-1?
```

### Search for Issues
```
Find all open issues assigned to me that are high priority
```

### Create a New Issue
```
Create a new bug report in the PROJECT with the summary "Login page is not working" and description "Users are unable to log in after the recent update."
```

### Record Work Time
```
Record 2 hours and 30 minutes of work time on issue PROJECT-123 with the description "Implemented the login feature"
```

## Configuration

The server can be configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `YOUTRACK_URL` | YouTrack instance URL | (required) |
| `YOUTRACK_API_TOKEN` | YouTrack permanent API token | (required) |
| `YOUTRACK_VERIFY_SSL` | Verify SSL certificates | `true` |
| `MCP_SERVER_NAME` | Name of the MCP server | `youtrack-mcp` |
| `MCP_SERVER_DESCRIPTION` | Description of the MCP server | `YouTrack MCP Server` |
| `MCP_DEBUG` | Enable debug logging | `false` |

## Architecture

This implementation uses **FastMCP 2.0** which provides:

- **Decorator-based tool definitions** - Clean, Pythonic code
- **Automatic schema generation** - From type hints and docstrings
- **Simplified architecture** - Single server instead of dual FastAPI/MCP setup
- **Modern MCP features** - Built on the latest MCP protocol standards

## Security Considerations

⚠️ **API Token Security**

- Never commit API tokens to repositories
- Use environment variables for credentials
- Rotate your YouTrack API tokens periodically
- Use tokens with minimum required permissions

## Requirements

- Docker
- YouTrack instance (Cloud or self-hosted)
- YouTrack API token with appropriate permissions