"""
FastMCP 2.0 implementation for YouTrack MCP Server.
"""
import json
import logging
from typing import Dict, List, Any, Optional

from fastmcp import FastMCP

from youtrack_mcp.config import config
from youtrack_mcp.api.client import YouTrackClient
from youtrack_mcp.api.issues import IssuesClient
from youtrack_mcp.api.projects import ProjectsClient
from youtrack_mcp.api.users import UsersClient
from youtrack_mcp.api.work_items import WorkItemsClient
from youtrack_mcp.api.search import SearchClient

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name=config.MCP_SERVER_NAME,
    description=config.MCP_SERVER_DESCRIPTION
)

# Initialize API clients
client = YouTrackClient()
issues_api = IssuesClient(client)
projects_api = ProjectsClient(client)
users_api = UsersClient(client)
work_items_api = WorkItemsClient(client)
search_api = SearchClient(client)


# Issue Tools
@mcp.tool()
def get_issue(issue_id: str) -> str:
    """
    Get information about a specific issue.
    
    Args:
        issue_id: The issue ID or readable ID (e.g., PROJECT-123)
        
    Returns:
        JSON string with issue information
    """
    try:
        fields = "id,summary,description,created,updated,project(id,name,shortName),reporter(id,login,name),assignee(id,login,name),customFields(id,name,value)"
        raw_issue = client.get(f"issues/{issue_id}?fields={fields}")
        
        if isinstance(raw_issue, dict) and raw_issue.get('$type') == 'Issue' and 'summary' not in raw_issue:
            raw_issue['summary'] = f"Issue {issue_id}"
        
        return json.dumps(raw_issue, indent=2)
        
    except Exception as e:
        logger.exception(f"Error getting issue {issue_id}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_issues(query: str, limit: int = 10) -> str:
    """
    Search for issues using YouTrack query language.
    
    Args:
        query: YouTrack search query (e.g., "project: MyProject state: Open")
        limit: Maximum number of issues to return (default: 10)
        
    Returns:
        JSON string with search results
    """
    try:
        results = issues_api.search_issues(query, limit)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.exception(f"Error searching issues with query: {query}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def create_issue(project_id: str, summary: str, description: str = "") -> str:
    """
    Create a new issue in a project.
    
    Args:
        project_id: The project ID or short name
        summary: Issue summary/title
        description: Issue description (optional)
        
    Returns:
        JSON string with created issue information
    """
    try:
        result = issues_api.create_issue(project_id, summary, description)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception(f"Error creating issue in project {project_id}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def add_comment(issue_id: str, text: str) -> str:
    """
    Add a comment to an issue.
    
    Args:
        issue_id: The issue ID or readable ID
        text: Comment text
        
    Returns:
        JSON string with comment information
    """
    try:
        result = issues_api.add_comment(issue_id, text)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception(f"Error adding comment to issue {issue_id}")
        return json.dumps({"error": str(e)})


# Project Tools
@mcp.tool()
def get_projects(include_archived: bool = False) -> str:
    """
    Get list of all projects.
    
    Args:
        include_archived: Whether to include archived projects (default: False)
        
    Returns:
        JSON string with projects list
    """
    try:
        results = projects_api.get_projects(include_archived)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.exception("Error getting projects")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_project(project_id: str) -> str:
    """
    Get details of a specific project.
    
    Args:
        project_id: The project ID or short name
        
    Returns:
        JSON string with project information
    """
    try:
        result = projects_api.get_project(project_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception(f"Error getting project {project_id}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_project_issues(project_id: str, limit: int = 20) -> str:
    """
    Get issues for a specific project.
    
    Args:
        project_id: The project ID or short name
        limit: Maximum number of issues to return (default: 20)
        
    Returns:
        JSON string with project issues
    """
    try:
        results = projects_api.get_project_issues(project_id, limit)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.exception(f"Error getting issues for project {project_id}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def create_project(name: str, short_name: str, description: str = "") -> str:
    """
    Create a new project.
    
    Args:
        name: Project name
        short_name: Project short name/key
        description: Project description (optional)
        
    Returns:
        JSON string with created project information
    """
    try:
        result = projects_api.create_project(name, short_name, description)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception(f"Error creating project {short_name}")
        return json.dumps({"error": str(e)})


# User Tools
@mcp.tool()
def get_current_user() -> str:
    """
    Get information about the current authenticated user.
    
    Returns:
        JSON string with user information
    """
    try:
        result = users_api.get_current_user()
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception("Error getting current user")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_user(user_id: str) -> str:
    """
    Get information about a specific user.
    
    Args:
        user_id: The user ID
        
    Returns:
        JSON string with user information
    """
    try:
        result = users_api.get_user(user_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception(f"Error getting user {user_id}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_users(query: str, limit: int = 10) -> str:
    """
    Search for users.
    
    Args:
        query: Search query for users
        limit: Maximum number of users to return (default: 10)
        
    Returns:
        JSON string with search results
    """
    try:
        results = users_api.search_users(query, limit)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.exception(f"Error searching users with query: {query}")
        return json.dumps({"error": str(e)})


# Work Items Tools
@mcp.tool()
def get_work_items(issue_id: str) -> str:
    """
    Get work items (time tracking entries) for a specific issue.
    
    Args:
        issue_id: The issue ID or readable ID
        
    Returns:
        JSON string with work items
    """
    try:
        results = work_items_api.get_work_items(issue_id)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.exception(f"Error getting work items for issue {issue_id}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def create_work_item(issue_id: str, duration: str, text: str = "") -> str:
    """
    Create a new work item for an issue (record time spent).
    
    Args:
        issue_id: The issue ID or readable ID
        duration: Time duration (e.g., "2h 30m", "1h", "45m")
        text: Work description (optional)
        
    Returns:
        JSON string with created work item information
    """
    try:
        result = work_items_api.create_work_item(issue_id, duration, text)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception(f"Error creating work item for issue {issue_id}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def update_work_item(issue_id: str, work_item_id: str, duration: str = None, text: str = None) -> str:
    """
    Update an existing work item.
    
    Args:
        issue_id: The issue ID or readable ID
        work_item_id: The work item ID
        duration: New time duration (optional)
        text: New work description (optional)
        
    Returns:
        JSON string with updated work item information
    """
    try:
        result = work_items_api.update_work_item(issue_id, work_item_id, duration, text)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception(f"Error updating work item {work_item_id} for issue {issue_id}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def delete_work_item(issue_id: str, work_item_id: str) -> str:
    """
    Delete a work item.
    
    Args:
        issue_id: The issue ID or readable ID
        work_item_id: The work item ID
        
    Returns:
        JSON string with deletion confirmation
    """
    try:
        result = work_items_api.delete_work_item(issue_id, work_item_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception(f"Error deleting work item {work_item_id} for issue {issue_id}")
        return json.dumps({"error": str(e)})


# Search Tools
@mcp.tool()
def advanced_search(query: str, sort_by: str = "created", sort_order: str = "desc", limit: int = 20) -> str:
    """
    Advanced search with sorting options.
    
    Args:
        query: Search query
        sort_by: Field to sort by (default: "created")
        sort_order: Sort order "asc" or "desc" (default: "desc")
        limit: Maximum number of results (default: 20)
        
    Returns:
        JSON string with search results
    """
    try:
        results = search_api.advanced_search(query, sort_by, sort_order, limit)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.exception(f"Error in advanced search with query: {query}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def filter_issues(project: str = None, assignee: str = None, state: str = None, priority: str = None, limit: int = 20) -> str:
    """
    Search with structured filtering.
    
    Args:
        project: Project name or ID (optional)
        assignee: Assignee login or name (optional)
        state: Issue state (optional)
        priority: Issue priority (optional)
        limit: Maximum number of results (default: 20)
        
    Returns:
        JSON string with filtered results
    """
    try:
        results = search_api.filter_issues(project, assignee, state, priority, limit)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.exception("Error in filter_issues")
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_with_custom_fields(custom_fields: Dict[str, str], limit: int = 20) -> str:
    """
    Search using custom field values.
    
    Args:
        custom_fields: Dictionary of custom field names and values
        limit: Maximum number of results (default: 20)
        
    Returns:
        JSON string with search results
    """
    try:
        results = search_api.search_with_custom_fields(custom_fields, limit)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.exception("Error in search_with_custom_fields")
        return json.dumps({"error": str(e)})


def get_server():
    """Get the FastMCP server instance."""
    return mcp


def close():
    """Close all connections."""
    if client:
        client.close()