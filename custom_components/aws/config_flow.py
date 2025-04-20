"""Config flow for AWS integration."""
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

# Constants
DEFAULT_REGION = "us-east-1"
CONF_AWS_ACCESS_KEY_ID = "aws_access_key_id"
CONF_AWS_SECRET_ACCESS_KEY = "aws_secret_access_key"
CONF_REGION_NAME = "region_name"


class AWSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AWS integration."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="AWS", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_AWS_ACCESS_KEY_ID): str,
            vol.Required(CONF_AWS_SECRET_ACCESS_KEY): str,
            vol.Required(CONF_REGION_NAME, default=DEFAULT_REGION): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> "AWSOptionsFlow":
        """Create the options flow."""
        return AWSOptionsFlow(config_entry)


class AWSOptionsFlow(config_entries.OptionsFlow):
    """AWS options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(
                CONF_REGION_NAME,
                default=self.config_entry.data.get(CONF_REGION_NAME, DEFAULT_REGION)
            ): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
