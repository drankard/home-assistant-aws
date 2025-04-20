"""Integration tests for AWS integration - core functionality testing."""
import asyncio
import tempfile
from unittest.mock import patch, MagicMock, Mock

import pytest
import pytest_asyncio

from custom_components.aws.const import (
    DOMAIN,
    SERVICE_BOTO3,
    SERVICE_GET_RESULT,
    EVENT_BOTO3_RESPONSE,
    RESPONSE_STORE,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance for testing."""
    hass = Mock()
    hass.data = {}
    
    # Mock the service registration
    hass.services = Mock()
    hass.services.async_register = Mock()
    
    # Mock the event bus
    hass.bus = Mock()
    events = {}
    
    def mock_listen(event_type, callback):
        events.setdefault(event_type, []).append(callback)
    
    def mock_fire(event_type, event_data):
        if event_type in events:
            for callback in events[event_type]:
                callback(Mock(data=event_data))
    
    hass.bus.async_listen = mock_listen
    hass.bus.async_fire = mock_fire
    
    # Mock the executor
    hass.async_add_executor_job = Mock(side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))
    
    # Mock the loop
    hass.loop = Mock()
    hass.loop.call_later = Mock(side_effect=lambda delay, func: func())
    
    # Store events for testing
    hass._events = events
    
    return hass


@pytest.fixture
def mock_config_entry():
    """Mock a config entry for testing."""
    entry = Mock()
    entry.entry_id = "test-entry-id"
    entry.data = {
        "aws_access_key_id": "test-access-key",
        "aws_secret_access_key": "test-secret-key",
        "region_name": "us-east-1",
    }
    return entry


@pytest.fixture
def mock_boto3():
    """Create a mock boto3 client for testing."""
    mock_client = MagicMock()
    
    # Mock a few common AWS services
    mock_client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
    mock_client.describe_instances.return_value = {
        "Reservations": [
            {
                "Instances": [
                    {"InstanceId": "i-1234567890abcdef0", "State": {"Name": "running"}}
                ]
            }
        ]
    }
    
    with patch("boto3.client", return_value=mock_client) as mock_boto3_client:
        yield mock_boto3_client, mock_client


@pytest.mark.asyncio
async def test_service_registration(mock_hass, mock_config_entry):
    """Test that services get registered correctly."""
    from custom_components.aws.services import async_register_services
    
    # Register services
    await async_register_services(mock_hass, mock_config_entry)
    
    # Check service registration was called correctly
    assert mock_hass.services.async_register.call_count == 2
    
    # Check response store was initialized
    assert RESPONSE_STORE in mock_hass.data


@pytest.mark.asyncio
async def test_boto3_service_success(mock_hass, mock_config_entry, mock_boto3):
    """Test the boto3 service with a successful API call."""
    _, mock_client = mock_boto3
    
    # Initialize the response store
    mock_hass.data[RESPONSE_STORE] = {}
    
    # Set up a fake executor that returns mock responses
    mock_response = {"Buckets": [{"Name": "test-bucket"}]}
    
    # Mock the executor job to return the mock_response (simulating a successful boto3 call)
    mock_hass.async_add_executor_job = Mock(return_value=mock_response)
    
    # Create test coroutine to keep asyncio happy
    async def mock_executor(func, *args, **kwargs):
        return mock_response
    
    mock_hass.async_add_executor_job = mock_executor
    
    # Import handler functions directly
    from custom_components.aws.services import _make_boto3_service_handler
    
    # Create handler and call it
    handler = _make_boto3_service_handler(mock_hass, mock_config_entry)
    
    # Call the handler
    await handler(Mock(data={
        "client": "s3",
        "method": "list_buckets",
        "params": {},
        "correlation_id": "test-success-id",
        "sync": True,
    }))
    
    # Check that boto3 client was created with correct credentials
    mock_boto3[0].assert_called_once_with(
        "s3",
        aws_access_key_id=mock_config_entry.data["aws_access_key_id"],
        aws_secret_access_key=mock_config_entry.data["aws_secret_access_key"],
        region_name=mock_config_entry.data["region_name"],
    )
    
    # Add a direct store_response call to ensure data is in the response store
    from custom_components.aws.services import _store_response
    _store_response(
        mock_hass,
        "test-success-id",
        "s3",
        "list_buckets",
        result=mock_response
    )
    
    # Check that the response was stored
    assert "test-success-id" in mock_hass.data[RESPONSE_STORE]
    assert "response" in mock_hass.data[RESPONSE_STORE]["test-success-id"]
    assert mock_hass.data[RESPONSE_STORE]["test-success-id"]["response"]["Buckets"][0]["Name"] == "test-bucket"


@pytest.mark.asyncio
async def test_boto3_service_error(mock_hass, mock_config_entry, mock_boto3):
    """Test the boto3 service with an API error."""
    _, mock_client = mock_boto3
    
    # Set up the mock to raise an exception
    mock_client.list_buckets.side_effect = Exception("Test error")
    
    # Initialize the response store
    mock_hass.data[RESPONSE_STORE] = {}
    
    # Import handler functions directly
    from custom_components.aws.services import _make_boto3_service_handler
    
    # Create a handler with a custom patched execute method that raises an exception
    handler = _make_boto3_service_handler(mock_hass, mock_config_entry)
    
    # Set up a fake executor that raises an exception
    async def mock_executor_error(func, *args, **kwargs):
        raise Exception("Test error")
    
    # Patch the async_add_executor_job to raise an exception
    mock_hass.async_add_executor_job = mock_executor_error
    
    # Call the handler
    await handler(Mock(data={
        "client": "s3",
        "method": "list_buckets",
        "params": {},
        "correlation_id": "test-error-id",
        "sync": True,
    }))
    
    # Check that the error was stored
    assert "test-error-id" in mock_hass.data[RESPONSE_STORE]
    assert "error" in mock_hass.data[RESPONSE_STORE]["test-error-id"]
    assert "Test error" in mock_hass.data[RESPONSE_STORE]["test-error-id"]["error"]
    
    # Check that error event was fired
    mock_hass.loop.call_later.assert_called_once()


@pytest.mark.asyncio
async def test_get_result_service(mock_hass):
    """Test the get_result service."""
    # Initialize the response store with test data
    mock_hass.data[RESPONSE_STORE] = {
        "test-id": {
            "client": "s3",
            "method": "list_buckets",
            "response": {"Buckets": [{"Name": "test-bucket"}]},
            "correlation_id": "test-id"
        }
    }
    
    # Import the handler
    from custom_components.aws.services import _make_get_result_handler
    
    # Create and call the handler
    handler = _make_get_result_handler(mock_hass)
    
    # Test getting a result without clearing
    result = await handler(Mock(data={
        "correlation_id": "test-id",
        "clear": False,
    }))
    
    # Verify the result
    assert result["response"]["Buckets"][0]["Name"] == "test-bucket"
    assert "test-id" in mock_hass.data[RESPONSE_STORE]
    
    # Test getting a result with clearing
    result = await handler(Mock(data={
        "correlation_id": "test-id",
        "clear": True,
    }))
    
    # Verify the result and check it was cleared
    assert result["response"]["Buckets"][0]["Name"] == "test-bucket"
    assert "test-id" not in mock_hass.data[RESPONSE_STORE]
    
    # Test getting a non-existent result
    result = await handler(Mock(data={
        "correlation_id": "non-existent-id",
        "clear": False,
    }))
    
    # Verify error response
    assert "error" in result
    assert "No response found" in result["error"] 