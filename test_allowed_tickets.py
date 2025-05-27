"""
Tests for allowed_tickets.py module.
"""
import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open
import sys

# Add the youtrack_mcp module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from youtrack_mcp.allowed_tickets import load_allowed_parent_tickets


class TestAllowedTickets(unittest.TestCase):
    """Test cases for the allowed_tickets module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_file = 'parent-ticket.json'
        
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_load_allowed_parent_tickets_file_not_exists(self):
        """Test loading when parent-ticket.json doesn't exist."""
        # Ensure file doesn't exist
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        result = load_allowed_parent_tickets()
        self.assertIsNone(result)
    
    def test_load_allowed_parent_tickets_valid_file(self):
        """Test loading with a valid parent-ticket.json file."""
        test_data = {
            "tickets": ["DEVOPS-123", "DEVOPS-456", "PROJECT-789"]
        }
        
        with open(self.test_file, 'w') as f:
            json.dump(test_data, f)
        
        result = load_allowed_parent_tickets()
        self.assertEqual(result, ["DEVOPS-123", "DEVOPS-456", "PROJECT-789"])
    
    def test_load_allowed_parent_tickets_empty_tickets(self):
        """Test loading with an empty tickets array."""
        test_data = {
            "tickets": []
        }
        
        with open(self.test_file, 'w') as f:
            json.dump(test_data, f)
        
        result = load_allowed_parent_tickets()
        self.assertIsNone(result)
    
    def test_load_allowed_parent_tickets_missing_tickets_key(self):
        """Test loading with a file missing the 'tickets' key."""
        test_data = {
            "other_key": "some_value"
        }
        
        with open(self.test_file, 'w') as f:
            json.dump(test_data, f)
        
        result = load_allowed_parent_tickets()
        self.assertIsNone(result)
    
    def test_load_allowed_parent_tickets_invalid_json(self):
        """Test loading with invalid JSON content."""
        with open(self.test_file, 'w') as f:
            f.write("invalid json content")
        
        result = load_allowed_parent_tickets()
        self.assertEqual(result, [])
    
    def test_load_allowed_parent_tickets_file_read_error(self):
        """Test handling of file read errors."""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError("Permission denied")
            
            # Mock os.path.exists to return True
            with patch('os.path.exists', return_value=True):
                result = load_allowed_parent_tickets()
                self.assertEqual(result, [])
    
    def test_load_allowed_parent_tickets_with_single_ticket(self):
        """Test loading with a single ticket."""
        test_data = {
            "tickets": ["DEVOPS-100"]
        }
        
        with open(self.test_file, 'w') as f:
            json.dump(test_data, f)
        
        result = load_allowed_parent_tickets()
        self.assertEqual(result, ["DEVOPS-100"])
    
    def test_load_allowed_parent_tickets_with_duplicate_tickets(self):
        """Test loading with duplicate ticket IDs."""
        test_data = {
            "tickets": ["DEVOPS-123", "DEVOPS-123", "DEVOPS-456"]
        }
        
        with open(self.test_file, 'w') as f:
            json.dump(test_data, f)
        
        result = load_allowed_parent_tickets()
        # The function should return the list as-is, including duplicates
        self.assertEqual(result, ["DEVOPS-123", "DEVOPS-123", "DEVOPS-456"])


if __name__ == '__main__':
    unittest.main()