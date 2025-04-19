from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, SERVICE_BOTO3, EVENT_BOTO3_RESPONSE
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import logging

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema({
    vol.Required("client"): cv.string,
    vol.Required("method"): cv.string,
    vol.Optional("params"): dict,
    vol.Optional("region_name"): cv.string,
    vol.Optional("sync", default=False): cv.boolean,
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True  # YAML not used


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = entry.data

    async def handle_boto3_service(call: ServiceCall):
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        client_name = call.data["client"]
        method_name = call.data["method"]
        params = call.data.get("params", {})
        region = call.data.get("region_name", entry.data["region_name"])
        sync = call.data.get("sync", False)

        try:
            client = boto3.client(
                client_name,
                aws_access_key_id=entry.data["aws_access_key_id"],
                aws_secret_access_key=entry.data["aws_secret_access_key"],
                region_name=region,
            )
            method = getattr(client, method_name)

            if sync:
                result = method(**params)
                _LOGGER.debug("AWS response: %s", result)
                hass.bus.async_fire(EVENT_BOTO3_RESPONSE, {
                    "client": client_name,
                    "method": method_name,
                    "response": result,
                })
            else:
                method(**params)

        except (BotoCoreError, ClientError, AttributeError) as e:
            _LOGGER.error("Failed to invoke %s.%s: %s", client_name, method_name, str(e))

    hass.services.async_register(
        DOMAIN, SERVICE_BOTO3, handle_boto3_service, schema=SERVICE_SCHEMA
    )

    return True
