"""AWS services for Home Assistant."""
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
import logging
import uuid
from .const import DOMAIN, SERVICE_BOTO3, EVENT_BOTO3_RESPONSE

_LOGGER = logging.getLogger(__name__)

async def async_register_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register services for AWS integration."""
    
    async def handle_boto3_service(call: ServiceCall):
        """Handle the boto3 service call."""
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        client_name = call.data["client"]
        method_name = call.data["method"]
        params = call.data.get("params", {})
        region = call.data.get("region_name", entry.data["region_name"])
        sync = call.data.get("sync", False)
        correlation_id = call.data.get("correlation_id", str(uuid.uuid4()))

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
                    "correlation_id": correlation_id
                })
            else:
                method(**params)

        except (BotoCoreError, ClientError, AttributeError) as e:
            _LOGGER.error("Failed to invoke %s.%s: %s", client_name, method_name, str(e))
            # Fire event even on error so automations can detect failures
            if sync:
                hass.bus.async_fire(EVENT_BOTO3_RESPONSE, {
                    "client": client_name,
                    "method": method_name,
                    "error": str(e),
                    "correlation_id": correlation_id
                })

    # Register the boto3 service
    hass.services.async_register(
        DOMAIN, SERVICE_BOTO3, handle_boto3_service, 
        schema=None  # Schema is defined in services.yaml
    ) 