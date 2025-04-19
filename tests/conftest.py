"""Test fixtures for AWS integration."""
import pytest
from unittest.mock import patch, MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.helpers.entity_registry import async_get
from custom_components.aws.const import DOMAIN

@pytest.fixture
def mock_boto3():
    """Mock boto3 client."""
    with patch("boto3.client") as mock_client:
        # Create a mock client that can be used in tests
        client = MagicMock()
        mock_client.return_value = client
        yield client

@pytest.fixture
async def hass(hass_storage):
    """Return a Home Assistant instance for testing."""
    hass = await async_get_test_instance()
    return hass

@pytest.fixture
async def aws_integration(hass):
    """Set up the AWS integration in Home Assistant."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "aws_access_key_id": "test-access-key",
            "aws_secret_access_key": "test-secret-key",
            "region_name": "us-east-1",
        },
        entry_id="test",
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry

# Additional imports needed for the fixtures
from homeassistant.const import CONF_PLATFORM
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from tests.async_mock import AsyncMock
from tests.common import MockConfigEntry

# Function to get a test instance
async def async_get_test_instance():
    """Return a Home Assistant instance for testing."""
    hass = HomeAssistant()
    hass.config.components.add("persistent_notification")
    await hass.async_start()
    return hass 