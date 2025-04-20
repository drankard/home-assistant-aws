"""AWS integration for Home Assistant."""
import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .services import async_register_services

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Dict[str, Any]) -> bool:
    """Set up the AWS component from YAML configuration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AWS from a config entry."""
    _LOGGER.debug("Setting up AWS integration from config entry")
    
    # Register services
    await async_register_services(hass, entry)
    
    # Store the entry for future reference
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading AWS integration config entry")
    
    # Remove this entry from hass data
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Clean up empty dictionaries
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    
    return True
