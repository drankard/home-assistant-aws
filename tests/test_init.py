"""Test AWS integration setup."""
from unittest.mock import patch
from homeassistant.setup import async_setup_component
from custom_components.aws.const import DOMAIN

async def test_async_setup(hass):
    """Test component setup."""
    with patch("custom_components.aws.async_setup_entry", return_value=True):
        assert await async_setup_component(hass, DOMAIN, {})

async def test_async_setup_entry(hass, aws_integration):
    """Test setting up the AWS integration through config flow."""
    # Integration was set up in the fixture
    assert DOMAIN in hass.data
    assert "aws_access_key_id" in hass.data[DOMAIN]
    assert hass.data[DOMAIN]["aws_access_key_id"] == "test-access-key"
    assert hass.data[DOMAIN]["aws_secret_access_key"] == "test-secret-key"
    assert hass.data[DOMAIN]["region_name"] == "us-east-1"

async def test_unload_entry(hass, aws_integration):
    """Test unloading the AWS integration."""
    assert DOMAIN in hass.data
    
    # Test unloading the entry
    assert await hass.config_entries.async_unload(aws_integration.entry_id)
    await hass.async_block_till_done()
    
    # Check that the data was removed
    assert DOMAIN not in hass.data 