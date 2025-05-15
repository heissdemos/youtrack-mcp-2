"""
YouTrack Work Items API client.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from youtrack_mcp.api.client import YouTrackClient


class WorkItem(BaseModel):
    """Model for a YouTrack work item."""
    
    id: Optional[str] = None
    issue_id: Optional[str] = None
    author: Optional[Dict[str, Any]] = None
    creator: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    duration: Dict[str, Any] = Field(default_factory=dict)
    date: Optional[int] = None  # Timestamp in milliseconds
    type: Optional[Dict[str, Any]] = None  # Work type
    created: Optional[int] = None
    updated: Optional[int] = None
    
    model_config = {
        "extra": "allow",  # Allow extra fields from the API
        "populate_by_name": True  # Allow population by field name
    }


class WorkItemsClient:
    """Client for interacting with YouTrack Work Items API."""
    
    def __init__(self, client: YouTrackClient):
        """
        Initialize the Work Items API client.
        
        Args:
            client: The YouTrack API client
        """
        self.client = client
    
    def get_work_items(self, issue_id: str) -> List[Dict[str, Any]]:
        """
        Get work items for an issue.
        
        Args:
            issue_id: The issue ID or readable ID (e.g., PROJECT-123)
            
        Returns:
            List of work items
        """
        response = self.client.get(f"issues/{issue_id}/timeTracking/workItems")
        return response
    
    def create_work_item(self, 
                         issue_id: str, 
                         duration: str,
                         text: Optional[str] = None,
                         work_type: Optional[str] = None,
                         date: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a new work item for an issue.
        
        Args:
            issue_id: The issue ID or readable ID (e.g., PROJECT-123)
            duration: The work duration in human-readable format (e.g., "1h 30m", "45m")
            text: Optional description of the work
            work_type: Optional work type ID
            date: Optional timestamp for the work item (defaults to current time)
            
        Returns:
            The created work item data
        """
        data = {
            "duration": {
                "presentation": duration
            }
        }
        
        if text:
            data["text"] = text
            
        if work_type:
            data["type"] = {"id": work_type}
            
        if date:
            data["date"] = date
        
        response = self.client.post(f"issues/{issue_id}/timeTracking/workItems", data=data)
        return response
    
    def update_work_item(self,
                         issue_id: str,
                         work_item_id: str,
                         duration: Optional[str] = None,
                         text: Optional[str] = None,
                         work_type: Optional[str] = None,
                         date: Optional[int] = None) -> Dict[str, Any]:
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
            The updated work item data
        """
        data = {}
        
        if duration:
            data["duration"] = {"presentation": duration}
            
        if text is not None:
            data["text"] = text
            
        if work_type:
            data["type"] = {"id": work_type}
            
        if date:
            data["date"] = date
            
        if not data:
            # Nothing to update
            return self.get_work_item(issue_id, work_item_id)
            
        response = self.client.post(f"issues/{issue_id}/timeTracking/workItems/{work_item_id}", data=data)
        return response
    
    def delete_work_item(self, issue_id: str, work_item_id: str) -> Dict[str, Any]:
        """
        Delete a work item.
        
        Args:
            issue_id: The issue ID or readable ID
            work_item_id: The ID of the work item to delete
            
        Returns:
            Empty response or error information
        """
        return self.client.delete(f"issues/{issue_id}/timeTracking/workItems/{work_item_id}")
    
    def get_work_item(self, issue_id: str, work_item_id: str) -> Dict[str, Any]:
        """
        Get a specific work item.
        
        Args:
            issue_id: The issue ID or readable ID
            work_item_id: The ID of the work item
            
        Returns:
            The work item data
        """
        response = self.client.get(f"issues/{issue_id}/timeTracking/workItems/{work_item_id}")
        return response