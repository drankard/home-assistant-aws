"""Test AWS service calls."""
from unittest.mock import patch, MagicMock
from custom_components.aws.const import DOMAIN, SERVICE_BOTO3, EVENT_BOTO3_RESPONSE

async def test_boto3_service(hass, aws_integration, mock_boto3):
    """Test calling the boto3 service."""
    # Set up a mock method on the boto3 client
    mock_boto3.list_buckets.return_value = {
        "Buckets": [
            {"Name": "test-bucket-1", "CreationDate": "2021-01-01T00:00:00Z"},
            {"Name": "test-bucket-2", "CreationDate": "2021-01-02T00:00:00Z"},
        ]
    }

    # Test calling the service asynchronously (no wait for response)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_BOTO3,
        {
            "client": "s3",
            "method": "list_buckets",
            "sync": False,
        },
        blocking=True,
    )
    
    # Verify boto3 was called
    mock_boto3.list_buckets.assert_called_once_with()
    
    # Reset the mock
    mock_boto3.list_buckets.reset_mock()
    
    # Set up an event listener to capture the response event
    event_data = None
    
    async def capture_event(event):
        """Capture the event data."""
        nonlocal event_data
        event_data = event.data
    
    hass.bus.async_listen(EVENT_BOTO3_RESPONSE, capture_event)
    
    # Test calling the service synchronously (wait for response)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_BOTO3,
        {
            "client": "s3",
            "method": "list_buckets",
            "sync": True,
        },
        blocking=True,
    )
    
    # Verify boto3 was called
    mock_boto3.list_buckets.assert_called_once_with()
    
    # Verify the event was fired with the expected data
    assert event_data is not None
    assert event_data["client"] == "s3"
    assert event_data["method"] == "list_buckets"
    assert event_data["response"]["Buckets"][0]["Name"] == "test-bucket-1"
    assert event_data["response"]["Buckets"][1]["Name"] == "test-bucket-2"

async def test_boto3_service_with_params(hass, aws_integration, mock_boto3):
    """Test calling the boto3 service with parameters."""
    # Set up a mock method on the boto3 client
    mock_boto3.list_objects.return_value = {
        "Contents": [
            {"Key": "test-key-1", "Size": 1024},
            {"Key": "test-key-2", "Size": 2048},
        ]
    }
    
    # Call the service with parameters
    await hass.services.async_call(
        DOMAIN,
        SERVICE_BOTO3,
        {
            "client": "s3",
            "method": "list_objects",
            "params": {
                "Bucket": "test-bucket",
                "Prefix": "test-prefix/",
            },
            "region_name": "us-west-2",  # Override the default region
            "sync": True,
        },
        blocking=True,
    )
    
    # Verify boto3 was called with the correct parameters
    mock_boto3.list_objects.assert_called_once_with(
        Bucket="test-bucket",
        Prefix="test-prefix/",
    ) 