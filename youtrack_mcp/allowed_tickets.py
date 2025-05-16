"""
Allowed parent tickets for time tracking in YouTrack MCP.

This module checks for a local file named 'parent-ticket.json' containing a list
of allowed parent ticket IDs. If the file exists, it uses those ticket IDs.
If no local file is found, all parent tickets are allowed.
"""
import os
import logging
import json

logger = logging.getLogger(__name__)

# Check for a local parent-ticket.json file
def load_allowed_parent_tickets():
    """
    Load allowed parent tickets from a local file if it exists.
    If the file doesn't exist, return None to indicate that all tickets are allowed.
    
    Returns:
        List of allowed ticket IDs or None if all tickets are allowed
    """
    parent_tickets_file = 'parent-ticket.json'
    
    if os.path.exists(parent_tickets_file):
        try:
            with open(parent_tickets_file, 'r') as f:
                # Read ticket IDs from JSON file
                data = json.load(f)
                tickets = data.get('tickets', [])
                logger.info(f"Loaded {len(tickets)} parent tickets from {parent_tickets_file}")
                return tickets
        except Exception as e:
            logger.error(f"Error reading parent tickets file: {str(e)}")
            # Return empty list if there's an error reading the file
            return []
    else:
        # If no file exists, return None to indicate all tickets are allowed
        logger.info(f"No {parent_tickets_file} found, all parent tickets will be allowed")
        return None

# Load parent tickets from file or use None (all tickets allowed)
ALLOWED_PARENT_TICKETS = load_allowed_parent_tickets()

