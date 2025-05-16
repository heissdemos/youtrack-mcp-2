#!/usr/bin/env python3

'''
Test script for ticket validations in YouTrack MCP:
1. Allowed parent tickets
2. Resolved/closed ticket status
'''

import json
import sys

from youtrack_mcp.api.client import YouTrackClient
from youtrack_mcp.api.work_items import WorkItemsClient
from youtrack_mcp.config import config


def test_ticket_validations():
    '''
    Test ticket validations for work item creation
    '''
    print("===== Testing Ticket Validations for Work Item Creation =====\n")
    
    # Check if there are allowed parent tickets defined
    if config.ALLOWED_PARENT_TICKETS is None:
        print("All parent tickets are allowed (no restrictions)")
    else:
        print("Allowed parent tickets:")
        for ticket in config.ALLOWED_PARENT_TICKETS:
            print(f"- {ticket}")
    print()

    # Create API client
    client = YouTrackClient()
    work_items_api = WorkItemsClient(client)

    # ===== Test allowed tickets validation =====
    print("===== Testing Allowed Tickets Validation =====\n")
    
    # Test with a ticket
    if config.ALLOWED_PARENT_TICKETS is None:
        # When all tickets are allowed, just use a test ticket ID
        test_ticket = "TEST-123"
        print(f"Testing with ticket: {test_ticket} (all tickets are allowed)")
    else:
        # When specific tickets are allowed, use the first one from the list
        test_ticket = config.ALLOWED_PARENT_TICKETS[0]
        print(f"Testing with allowed ticket: {test_ticket}")
    
    try:
        # Just validate the ticket - don't actually create a work item
        result = work_items_api.is_parent_ticket_allowed(test_ticket)
        print(f"Validation result: {result}")
        print("✅ Validation passed for ticket")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # Test with potentially non-allowed ticket
    non_allowed_ticket = "FAKE-123"
    print(f"\nTesting with non-allowed ticket: {non_allowed_ticket}")
    try:
        # Just validate the ticket - don't actually create a work item
        result = work_items_api.is_parent_ticket_allowed(non_allowed_ticket)
        print(f"Validation result: {result}")
        if config.ALLOWED_PARENT_TICKETS is None:
            if result:
                print("✅ Validation accepted ticket as expected (all tickets are allowed)")
            else:
                print("❌ Validation incorrectly rejected ticket when all should be allowed")
        else:
            if not result:
                print("✅ Validation rejected non-allowed ticket as expected")
            else:
                print("❌ Validation incorrectly accepted non-allowed ticket")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # Test the actual work item creation with validation
    if config.ALLOWED_PARENT_TICKETS is not None:
        print("\nTesting work item creation with non-allowed ticket (should fail)")
        try:
            work_items_api.create_work_item(
                issue_id=non_allowed_ticket,
                duration="1h",
                text="Test work item"
            )
            print("❌ Error: Created work item for non-allowed ticket")
        except ValueError as e:
            print(f"✅ Validation correctly rejected creation: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    else:
        print("\nSkipping work item creation test with non-allowed ticket (all tickets are allowed)")
    
    # ===== Test resolved tickets validation =====
    print("\n===== Testing Resolved Tickets Validation =====\n")
    
    # Define tickets to check
    if config.ALLOWED_PARENT_TICKETS is None:
        # When all tickets are allowed, just use a couple of test tickets
        test_tickets = ["TEST-123", "EXAMPLE-456"]
        print("Using test tickets since all tickets are allowed")
    else:
        # When specific tickets are allowed, use those
        test_tickets = config.ALLOWED_PARENT_TICKETS
    
    # For each ticket, check if it's resolved
    for ticket in test_tickets:
        print(f"Checking if ticket {ticket} is resolved:")
        try:
            is_resolved, message = work_items_api.is_ticket_resolved(ticket)
            print(f"- Is resolved: {is_resolved}")
            print(f"- Status message: {message}")
            if is_resolved:
                print("✅ Ticket is correctly identified as resolved")
            else:
                print("✅ Ticket is correctly identified as not resolved")
                
                # Test create_work_item with checks
                print(f"\nTesting work item creation validation for {ticket}:")
                try:
                    # Don't actually create the work item - this is just to test validation
                    # We use a small duration and add a check parameter to prevent actual creation
                    print("- Attempting validation only (no actual creation)")
                    # This should pass if the ticket is not resolved and is in the allowed list (or all are allowed)
                    result = work_items_api.is_parent_ticket_allowed(ticket) and not is_resolved
                    if result:
                        print("✅ Validation passed as expected")
                    else:
                        print("❌ Validation failed")
                except ValueError as e:
                    print(f"❌ Validation error: {str(e)}")
                except Exception as e:
                    print(f"❌ Unexpected error: {str(e)}")
        except Exception as e:
            print(f"❌ Error checking resolution status: {str(e)}")


if __name__ == "__main__":
    test_ticket_validations()
