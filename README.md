# YouTrack MCP Server

A Model Context Protocol (MCP) server implementation for JetBrains YouTrack, allowing AI assistants to interact with YouTrack issue tracking system.

![Screenshot](screenshot/CleanShot%202025-04-14%20at%2023.24.21@2x.png)

## What is MCP?

Model Context Protocol (MCP) is an open standard that enables AI models to interact with external tools and services through a unified interface. This project provides an MCP server that exposes YouTrack functionality to AI assistants that support the MCP standard, such as Claude in VS Code and GitHub Copilot in agent mode.

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
  - Manage custom fields

- **User Management**
  - Get current user information
  - Search for users
  - Access user details and groups

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

The recommended way to run the YouTrack MCP server is using Docker:

1. Clone the repository:
   ```
   git clone https://github.com/tonyzorin/youtrack-mcp.git
   cd youtrack-mcp
   ```

2. Build the Docker image:
   ```
   docker build -t youtrack-mcp .
   ```

3. Run the container with your YouTrack credentials:
   ```
   docker run -i --rm \
     -e YOUTRACK_URL=https://your-instance.youtrack.cloud \
     -e YOUTRACK_API_TOKEN=your-api-token \
     youtrack-mcp
   ```

   Note: The `-i` flag is important as it keeps STDIN open, which is required for the MCP stdio transport.

### Security Considerations

⚠️ **API Token Security**

- Treat your mcp.json file as .env
- Rotate your YouTrack API tokens periodically
- Use tokens with the minimum required permissions for your use case


## Using with Cursor

To use your YouTrack MCP server with Cursor:

1. Make sure you have the Docker image built:
   ```
   docker build -t youtrack-mcp .
   ```

2. Create a `.cursor/mcp.json` file with the following content:

    ```json
    {
        "mcpServers": {
            "YouTrack": {
                "type": "stdio",
                "command": "docker",
                "args": ["run", "-i", "--rm", 
                "-e", "YOUTRACK_URL=https://yourinstance.youtrack.cloud",
                "-e", "YOUTRACK_API_TOKEN=perm:your-token",
                "youtrack-mcp"
                ]
            }
        }
    }
    ```
Replace `yourinstance.youtrack.cloud` with your actual YouTrack instance URL and `perm:your-token` with your actual API token.



## Using with VS Code

To use the YouTrack MCP server with VS Code:

1. Make sure you have the Docker image built:
   ```
   docker build -t youtrack-mcp .
   ```

2. Create a `.vscode/mcp.json` file with the following content:

   ```json
   {
     "servers": {
       "YouTrack": {
         "type": "stdio",
         "command": "docker",
         "args": ["run", "-i", "--rm", 
           "-e", "YOUTRACK_URL=https://yourinstance.youtrack.cloud",
           "-e", "YOUTRACK_API_TOKEN=perm:your-token",
           "youtrack-mcp"
         ]
       }
     }
   }
   ```

   Replace `yourinstance.youtrack.cloud` with your actual YouTrack instance URL and `perm:your-token` with your actual API token.

## Available Tools

The YouTrack MCP server provides the following tools:

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
- `get_user_by_login` - Find a user by login name
- `get_user_groups` - Get groups for a user

### Time Tracking

- `get_work_items` - Get work items (time tracking entries) for a specific issue
- `create_work_item` - Create a new work item for an issue (record time spent)
- `update_work_item` - Update an existing work item
- `delete_work_item` - Delete a work item
- `get_work_item` - Get details of a specific work item

Time tracking is protected by two validation mechanisms:
1. **Allowed Tickets**: Only tickets in the approved list (ALLOWED_PARENT_TICKETS) can receive time entries
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

### Add a Comment

```
Add a comment to issue PROJECT-456 saying "I've fixed this issue in the latest commit. Please review."
```

### Record Work Time

```
Record 2 hours and 30 minutes of work time on issue PROJECT-123 with the description "Implemented the login feature"
```

Note: Work time can only be recorded on:
1. Tickets in the approved list (configured in ALLOWED_PARENT_TICKETS)
2. Tickets that are not in a resolved/closed state

### Get Time Tracking Entries

```
Show me all the time entries for issue PROJECT-123 from this week
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
| `ALLOWED_PARENT_TICKETS` | List of ticket IDs allowed for time tracking | (configured in allowed_tickets.py) |

### SSL Certificate Verification

For self-hosted instances with self-signed SSL certificates, you can disable SSL verification:

```bash
docker run -i --rm \
  -e YOUTRACK_URL=https://youtrack.internal.company.com \
  -e YOUTRACK_API_TOKEN=perm:your-permanent-token \
  -e YOUTRACK_VERIFY_SSL=false \
  youtrack-mcp
```

This option is only recommended for development or in controlled environments where you cannot add the certificate to the trust store.

### Debug Mode

You can enable debug logging for troubleshooting:

```bash
docker run -i --rm \
  -e YOUTRACK_URL=https://yourinstance.youtrack.cloud \
  -e YOUTRACK_API_TOKEN=perm:your-permanent-token \
  -e MCP_DEBUG=true \
  youtrack-mcp
```