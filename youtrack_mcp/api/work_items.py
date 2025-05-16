"""
YouTrack Work Items API client.
"""
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from youtrack_mcp.api.client import YouTrackClient
from youtrack_mcp.allowed_tickets import ALLOWED_PARENT_TICKETS


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
    
    def is_parent_ticket_allowed(self, issue_id: str) -> bool:
        """
        Check if the given issue ID is in the list of allowed parent tickets.
        
        Args:
            issue_id: The issue ID to check
            
        Returns:
            True if the issue ID is in the allowed list, False otherwise
        """
        return issue_id in ALLOWED_PARENT_TICKETS
        
    def is_ticket_resolved(self, issue_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the ticket is resolved (closed) in YouTrack.
        
        Examines the ticket's state fields to determine if all of them are marked as resolved.
        If any state field is not resolved, the ticket is considered open.
        
        Args:
            issue_id: The issue ID or readable ID (e.g., PROJECT-123)
            
        Returns:
            A tuple containing:
            - A boolean indicating if the ticket is resolved (True) or not (False)
            - An optional string message with details (state name or error message)
        """
        try:
            # Fetch the issue details from the API with fields that include state information
            fields = "$type,id,summary,customFields($type,id,name,value($type,id,name,isResolved))"
            response = self.client.get(f"issues/{issue_id}?fields={fields}")
            
            # Check if the response contains the necessary fields
            if "customFields" not in response:
                return False, "Could not fetch state fields for the issue"
                
            # Look for state-type fields and check if all are resolved
            state_fields = [field for field in response["customFields"] 
                           if field.get("$type", "").endswith("StateIssueCustomField")]
            
            # If no state fields found, assume the ticket is open
            if not state_fields:
                return False, "No state fields found for the issue"
                
            # Check each state field for resolution status
            for field in state_fields:
                if "value" in field and field["value"] is not None:
                    value = field["value"]
                    is_resolved = value.get("isResolved", False)
                    field_name = field.get("name", "State")
                    state_name = value.get("name", "Unknown")
                    
                    # If any state field is not resolved, the ticket is considered open
                    if not is_resolved:
                        return False, f"Issue has state '{state_name}' in field '{field_name}' which is not resolved"
                else:
                    # If a state field has no value, consider it not resolved
                    field_name = field.get("name", "State")
                    return False, f"Issue has no value for state field '{field_name}'"
            
            # If we reach here, all state fields are resolved
            return True, "All state fields are resolved"
            
        except Exception as e:
            # In case of error, assume the ticket is open
            return False, f"Error checking ticket status: {str(e)}"
    
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
            
        Raises:
            ValueError: If the issue ID is not in the list of allowed parent tickets
            ValueError: If the issue is resolved/closed and time tracking is not allowed
        """
        # Check if the issue ID is in the allowed list
        if not self.is_parent_ticket_allowed(issue_id):
            allowed_tickets = ", ".join(ALLOWED_PARENT_TICKETS)
            raise ValueError(f"Issue ID '{issue_id}' is not in the list of allowed parent tickets. Allowed tickets: {allowed_tickets}")
        
        # Check if the ticket is resolved (closed)
        is_resolved, message = self.is_ticket_resolved(issue_id)
        if is_resolved:
            raise ValueError(f"Cannot add work items to resolved ticket '{issue_id}'. Status: {message}")
        
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