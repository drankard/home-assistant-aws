import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class AWSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="AWS", data=user_input)

        schema = vol.Schema({
            vol.Required("aws_access_key_id"): str,
            vol.Required("aws_secret_access_key"): str,
            vol.Required("region_name", default="us-east-1"): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AWSOptionsFlow(config_entry)


class AWSOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(
                "region_name",
                default=self.config_entry.data.get("region_name", "us-east-1")
            ): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
