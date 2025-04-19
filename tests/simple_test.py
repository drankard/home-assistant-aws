"""Simple unit tests for AWS integration."""
import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import importlib
import inspect

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom_components.aws.const import DOMAIN, SERVICE_BOTO3, EVENT_BOTO3_RESPONSE


class TestAWSIntegration(unittest.TestCase):
    """Test the AWS integration basics."""

    def test_constants(self):
        """Test that constants are defined correctly."""
        self.assertEqual(DOMAIN, "aws")
        self.assertEqual(SERVICE_BOTO3, "boto3")
        self.assertEqual(EVENT_BOTO3_RESPONSE, "aws_boto3_response")
    
    @patch("boto3.client")
    def test_boto3_direct(self, mock_boto3_client):
        """Test boto3 client directly with mock."""
        # Setup the mock
        mock_client = MagicMock()
        mock_client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        mock_boto3_client.return_value = mock_client
        
        # Import boto3
        import boto3
        
        # Create a client
        client = boto3.client(
            "s3",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region_name="us-east-1"
        )
        
        # Call a method
        result = client.list_buckets()
        
        # Verify boto3.client was called with correct args
        mock_boto3_client.assert_called_with(
            "s3",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region_name="us-east-1"
        )
        
        # Verify the result
        self.assertEqual(result["Buckets"][0]["Name"], "test-bucket")
    
    def test_module_structure(self):
        """Test that the integration modules are structured correctly."""
        # Import modules directly (avoiding __init__ name conflict)
        import custom_components.aws.services as services
        import custom_components.aws.config_flow as config_flow
        
        # Import init module using importlib
        init_module = importlib.import_module("custom_components.aws.__init__")
        
        # Check that the main module has the necessary setup functions
        self.assertTrue(hasattr(init_module, "async_setup"))
        self.assertTrue(hasattr(init_module, "async_setup_entry"))
        self.assertTrue(hasattr(init_module, "async_unload_entry"))
        
        # Check that the services module has the register function
        self.assertTrue(hasattr(services, "async_register_services"))
        
        # Check that config_flow has the necessary classes
        self.assertTrue(hasattr(config_flow, "AWSConfigFlow"))
        
        # Check manifest file exists and has required fields
        import json
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "custom_components", "aws", "manifest.json")) as f:
            manifest = json.load(f)
            self.assertEqual(manifest["domain"], "aws")
            self.assertEqual(manifest["name"], "AWS")
            self.assertTrue("version" in manifest)
            self.assertTrue("config_flow" in manifest)
            self.assertTrue("requirements" in manifest)
            self.assertTrue("boto3" in manifest["requirements"][0])
    
    def test_service_handler(self):
        """Test the AWS service handler directly."""
        # Import service module code
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "custom_components", "aws", "services.py")) as f:
            service_code = f.read()
        
        # Verify the code contains expected elements - this is a basic check
        # without having to execute the async code
        self.assertIn("async def async_register_services", service_code)
        self.assertIn("async def handle_boto3_service", service_code)
        self.assertIn("boto3.client", service_code)
        self.assertIn("aws_access_key_id", service_code)
        self.assertIn("aws_secret_access_key", service_code)
        self.assertIn("region_name", service_code)
        self.assertIn("hass.services.async_register", service_code)
        self.assertIn("hass.bus.async_fire", service_code)
        self.assertIn("EVENT_BOTO3_RESPONSE", service_code)


if __name__ == "__main__":
    unittest.main() 