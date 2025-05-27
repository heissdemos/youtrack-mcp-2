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
        If ALLOWED_PARENT_TICKETS is None or empty, all tickets are allowed.
        
        Args:
            issue_id: The issue ID to check
            
        Returns:
            True if the issue ID is in the allowed list or if all tickets are allowed,
            False otherwise
        """
        # If ALLOWED_PARENT_TICKETS is None or empty, all tickets are allowed
        if ALLOWED_PARENT_TICKETS is None or len(ALLOWED_PARENT_TICKETS) == 0:
            return True
        
        # Otherwise, check if the issue ID is in the allowed list
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
    
    def is_time_tracking_enabled(self, issue_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if time tracking is enabled for the issue's project.
        
        Args:
            issue_id: The issue ID or readable ID (e.g., PROJECT-123)
            
        Returns:
            A tuple containing:
            - A boolean indicating if time tracking is enabled
            - An optional string message with details
        """
        try:
            # Get issue details with project information
            fields = "id,project(id,name,shortName)"
            issue_response = self.client.get(f"issues/{issue_id}?fields={fields}")
            
            if "project" not in issue_response:
                return False, "Could not fetch project information for the issue"
            
            project = issue_response["project"]
            project_id = project.get("id") or project.get("shortName")
            
            if not project_id:
                return False, "Could not determine project ID"
            
            # Try to get time tracking settings for the project
            try:
                # Check if we can access time tracking by trying to get work items
                self.client.get(f"issues/{issue_id}/timeTracking/workItems?$top=1")
                return True, "Time tracking is available"
            except Exception as e:
                error_str = str(e).lower()
                if "400" in error_str or "bad request" in error_str:
                    project_name = project.get("name") or project.get("shortName", "Unknown")
                    return False, f"Time tracking is disabled for project '{project_name}'. Please enable it in YouTrack project settings."
                else:
                    return False, f"Error checking time tracking availability: {str(e)}"
                    
        except Exception as e:
            return False, f"Error checking time tracking settings: {str(e)}"

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
            ValueError: If time tracking is disabled for the project
        """
        # Check if the issue ID is in the allowed list
        if not self.is_parent_ticket_allowed(issue_id):
            # If ALLOWED_PARENT_TICKETS is not None and not empty, show the list of allowed tickets
            if ALLOWED_PARENT_TICKETS is not None and len(ALLOWED_PARENT_TICKETS) > 0:
                allowed_tickets = ", ".join(ALLOWED_PARENT_TICKETS)
                raise ValueError(f"Issue ID '{issue_id}' is not in the list of allowed parent tickets. Allowed tickets: {allowed_tickets}")
            else:
                # This should never happen, but just in case
                raise ValueError(f"Issue ID '{issue_id}' is not allowed, but no restrictions are defined. This is unexpected.")
        
        # Check if time tracking is enabled for this project
        time_tracking_enabled, time_tracking_message = self.is_time_tracking_enabled(issue_id)
        if not time_tracking_enabled:
            raise ValueError(f"Cannot create work item for '{issue_id}': {time_tracking_message}")
        
        # Check if the ticket is resolved (closed)
        is_resolved, message = self.is_ticket_resolved(issue_id)
        if is_resolved:
            raise ValueError(f"Cannot add work items to resolved ticket '{issue_id}'. Status: {message}")
        
        # Try different common formats that work with YouTrack
        data_formats = [
            # Format 1: Standard YouTrack format with presentation
            {
                "duration": {"presentation": duration}
            },
            # Format 2: Direct duration string
            {
                "duration": duration
            },
            # Format 3: Duration with minutes conversion
            self._convert_to_minutes_format(duration)
        ]
        
        # Add optional fields to all formats
        for data in data_formats:
            if data is None:
                continue
            if text:
                data["text"] = text
            if work_type:
                data["type"] = {"id": work_type}
            if date:
                data["date"] = date
        
        # Alternative: Use direct HTTP client approach
        import requests
        import json
        from youtrack_mcp.config import config
        
        # Build direct request
        url = f"{config.get_base_url()}/issues/{issue_id}/timeTracking/workItems"
        headers = {
            "Authorization": f"Bearer {config.YOUTRACK_API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Try with simple duration format first
        simple_data = {"duration": {"presentation": duration}}
        if text:
            simple_data["text"] = text
        
        try:
            response = requests.post(url, json=simple_data, headers=headers, verify=config.VERIFY_SSL)
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            elif response.status_code == 400:
                # Try alternative formats
                for alt_data in [
                    {"duration": duration, "text": text} if text else {"duration": duration},
                    {"duration": {"minutes": self._parse_duration_to_minutes(duration)}, "text": text} if text else {"duration": {"minutes": self._parse_duration_to_minutes(duration)}}
                ]:
                    alt_response = requests.post(url, json=alt_data, headers=headers, verify=config.VERIFY_SSL)
                    if alt_response.status_code in [200, 201]:
                        return alt_response.json()
                
                # If all failed, raise with details
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            else:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {str(e)}")
    
    def _parse_duration_to_minutes(self, duration: str) -> int:
        """Parse duration string to total minutes."""
        try:
            import re
            total_minutes = 0
            hours_match = re.search(r'(\d+)h', duration.lower())
            minutes_match = re.search(r'(\d+)m', duration.lower())
            
            if hours_match:
                total_minutes += int(hours_match.group(1)) * 60
            if minutes_match:
                total_minutes += int(minutes_match.group(1))
            
            if total_minutes == 0:
                number_match = re.search(r'(\d+)', duration)
                if number_match:
                    total_minutes = int(number_match.group(1))
            
            return total_minutes if total_minutes > 0 else 60  # Default to 1 hour
        except:
            return 60  # Default fallback
    
    def _convert_to_minutes_format(self, duration: str) -> Optional[Dict[str, Any]]:
        """
        Convert duration string to minutes format.
        
        Args:
            duration: Duration string like "2h", "30m", "1h 30m"
            
        Returns:
            Dictionary with minutes format or None if conversion fails
        """
        try:
            import re
            total_minutes = 0
            
            # Parse hours and minutes from duration string
            hours_match = re.search(r'(\d+)h', duration.lower())
            minutes_match = re.search(r'(\d+)m', duration.lower())
            
            if hours_match:
                total_minutes += int(hours_match.group(1)) * 60
            if minutes_match:
                total_minutes += int(minutes_match.group(1))
            
            # If no time found, try parsing as pure number (assume minutes)
            if total_minutes == 0:
                number_match = re.search(r'(\d+)', duration)
                if number_match:
                    total_minutes = int(number_match.group(1))
            
            if total_minutes > 0:
                return {
                    "duration": {
                        "minutes": total_minutes
                    }
                }
            return None
        except:
            return None
    
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