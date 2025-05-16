"""
YouTrack Work Items MCP tools.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from youtrack_mcp.api.client import YouTrackClient
from youtrack_mcp.api.work_items import WorkItemsClient

logger = logging.getLogger(__name__)


class WorkItemTools:
    """Work item-related MCP tools."""
    
    def __init__(self):
        """Initialize the work item tools."""
        self.client = YouTrackClient()
        self.work_items_api = WorkItemsClient(self.client)
        
    def get_work_items(self, issue_id: str) -> str:
        """
        Get work items for a specific issue.
        
        Args:
            issue_id: The issue ID or readable ID (e.g., PROJECT-123)
            
        Returns:
            JSON string with work items information
        """
        try:
            raw_work_items = self.work_items_api.get_work_items(issue_id)
            return json.dumps(raw_work_items, indent=2)
        except Exception as e:
            logger.exception(f"Error getting work items for issue {issue_id}")
            return json.dumps({"error": str(e)})
    
    def create_work_item(self, issue_id: str, duration: str, text: Optional[str] = None, 
                         work_type: Optional[str] = None, date: Optional[int] = None) -> str:
        """
        Create a new work item for an issue.
        
        Args:
            issue_id: The issue ID or readable ID (e.g., PROJECT-123)
            duration: The work duration in human-readable format (e.g., "1h 30m", "45m")
            text: Optional description of the work
            work_type: Optional work type ID
            date: Optional timestamp for the work item (defaults to current time)
            
        Returns:
            JSON string with the created work item information
        """
        try:
            # Validation occurs inside the API client method
            result = self.work_items_api.create_work_item(
                issue_id=issue_id,
                duration=duration,
                text=text,
                work_type=work_type,
                date=date
            )
            return json.dumps(result, indent=2)
        except ValueError as e:
            # Specific handling for validation errors (not allowed parent ticket)
            logger.warning(f"Validation error creating work item for issue {issue_id}: {str(e)}")
            return json.dumps({"error": str(e), "type": "validation_error"})
        except Exception as e:
            # General error handling
            logger.exception(f"Error creating work item for issue {issue_id}")
            return json.dumps({"error": str(e)})
    
    def update_work_item(self, issue_id: str, work_item_id: str, duration: Optional[str] = None,
                         text: Optional[str] = None, work_type: Optional[str] = None, 
                         date: Optional[int] = None) -> str:
        """
        Update an existing work item.
        
        Args:
            issue_id: The issue ID or readable ID
            work_item_id: The ID of the work item to update
            duration: The new work duration in human-readable format (e.g., "1h 30m", "45m")
            text: The new description of the work
            work_type: The new work type ID
            date: The new timestamp for the work item
            
        Returns:
            JSON string with the updated work item information
        """
        try:
            result = self.work_items_api.update_work_item(
                issue_id=issue_id,
                work_item_id=work_item_id,
                duration=duration,
                text=text,
                work_type=work_type,
                date=date
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.exception(f"Error updating work item {work_item_id} for issue {issue_id}")
            return json.dumps({"error": str(e)})
    
    def delete_work_item(self, issue_id: str, work_item_id: str) -> str:
        """
        Delete a work item.
        
        Args:
            issue_id: The issue ID or readable ID
            work_item_id: The ID of the work item to delete
            
        Returns:
            JSON string with the result
        """
        try:
            result = self.work_items_api.delete_work_item(issue_id, work_item_id)
            return json.dumps({"success": True, "message": "Work item deleted successfully"}, indent=2)
        except Exception as e:
            logger.exception(f"Error deleting work item {work_item_id} for issue {issue_id}")
            return json.dumps({"error": str(e)})
    
    def get_work_item(self, issue_id: str, work_item_id: str) -> str:
        """
        Get a specific work item.
        
        Args:
            issue_id: The issue ID or readable ID
            work_item_id: The ID of the work item
            
        Returns:
            JSON string with work item information
        """
        try:
            raw_work_item = self.work_items_api.get_work_item(issue_id, work_item_id)
            return json.dumps(raw_work_item, indent=2)
        except Exception as e:
            logger.exception(f"Error getting work item {work_item_id} for issue {issue_id}")
            return json.dumps({"error": str(e)})
    
    def close(self) -> None:
        """Close the API client."""
        self.client.close()
        
    def get_tool_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the definitions of all work item tools.
        
        Returns:
            Dictionary mapping tool names to their configuration
        """
        return {
            "work_items.get_work_items": {
                "function": self.get_work_items,
                "description": "Get work items for a specific YouTrack issue",
                "parameter_descriptions": {
                    "issue_id": "The issue ID or readable ID (e.g., PROJECT-123)"
                }
            },
            "work_items.create_work_item": {
                "function": self.create_work_item,
                "description": "Create a new work item (time tracking entry) for a YouTrack issue",
                "parameter_descriptions": {
                    "issue_id": "The issue ID or readable ID (e.g., PROJECT-123)",
                    "duration": "The work duration in human-readable format (e.g., '1h 30m', '45m')",
                    "text": "Optional description of the work",
                    "work_type": "Optional work type ID",
                    "date": "Optional timestamp for the work item (defaults to current time)"
                }
            },
            "work_items.update_work_item": {
                "function": self.update_work_item,
                "description": "Update an existing work item in a YouTrack issue",
                "parameter_descriptions": {
                    "issue_id": "The issue ID or readable ID",
                    "work_item_id": "The ID of the work item to update",
                    "duration": "The new work duration in human-readable format (e.g., '1h 30m', '45m')",
                    "text": "The new description of the work",
                    "work_type": "The new work type ID",
                    "date": "The new timestamp for the work item"
                }
            },
            "work_items.delete_work_item": {
                "function": self.delete_work_item,
                "description": "Delete a work item from a YouTrack issue",
                "parameter_descriptions": {
                    "issue_id": "The issue ID or readable ID",
                    "work_item_id": "The ID of the work item to delete"
                }
            },
            "work_items.get_work_item": {
                "function": self.get_work_item,
                "description": "Get a specific work item from a YouTrack issue",
                "parameter_descriptions": {
                    "issue_id": "The issue ID or readable ID",
                    "work_item_id": "The ID of the work item"
                }
            }
        }