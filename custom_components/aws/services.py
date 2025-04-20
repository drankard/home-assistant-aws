"""AWS services for Home Assistant."""
import logging
import uuid
from typing import Any, Dict, Optional, Callable

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from .const import (
    DOMAIN,
    EVENT_BOTO3_RESPONSE,
    RESPONSE_STORE,
    SERVICE_BOTO3,
    SERVICE_GET_RESULT,
)

_LOGGER = logging.getLogger(__name__)


async def async_register_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register services for AWS integration."""
    # Initialize response store if it doesn't exist
    if RESPONSE_STORE not in hass.data:
        hass.data[RESPONSE_STORE] = {}
    
    hass.services.async_register(
        DOMAIN, 
        SERVICE_BOTO3, 
        _make_boto3_service_handler(hass, entry),
        schema=None  # Schema is defined in services.yaml
    )
    
    hass.services.async_register(
        DOMAIN, 
        SERVICE_GET_RESULT, 
        _make_get_result_handler(hass),
        schema=None,  # Schema is defined in services.yaml
        supports_response=True
    )


def _make_boto3_service_handler(hass: HomeAssistant, entry: ConfigEntry) -> Callable:
    """Create a handler for the boto3 service."""
    
    async def handle_boto3_service(call: ServiceCall) -> None:
        """Handle the boto3 service call."""
        # Extract parameters from service call
        client_name = call.data["client"]
        method_name = call.data["method"]
        params = call.data.get("params", {})
        region = call.data.get("region_name", entry.data["region_name"])
        sync = call.data.get("sync", False)
        correlation_id = call.data.get("correlation_id", str(uuid.uuid4()))
        
        _LOGGER.info(
            "Executing %s.%s (correlation_id: %s)", 
            client_name, 
            method_name, 
            correlation_id
        )
        
        try:
            # Initialize boto3 client
            client = boto3.client(
                client_name,
                aws_access_key_id=entry.data["aws_access_key_id"],
                aws_secret_access_key=entry.data["aws_secret_access_key"],
                region_name=region,
            )
            method = getattr(client, method_name)
            
            await _execute_aws_method(
                hass=hass,
                method=method,
                params=params,
                client_name=client_name,
                method_name=method_name,
                correlation_id=correlation_id,
                sync=sync
            )
                
        except (BotoCoreError, ClientError, AttributeError) as error:
            # Handle boto3 client setup errors
            _LOGGER.error(
                "Failed to initialize %s.%s: %s", 
                client_name, 
                method_name, 
                str(error)
            )
            
            # Store error response and potentially fire event
            _handle_error(
                hass=hass,
                error=error,
                client_name=client_name,
                method_name=method_name,
                correlation_id=correlation_id,
                sync=sync
            )

    return handle_boto3_service


def _make_get_result_handler(hass: HomeAssistant) -> Callable:
    """Create a handler for the get_result service."""
    
    async def handle_get_result(call: ServiceCall) -> Dict[str, Any]:
        """Get a result from a previous boto3 call."""
        correlation_id = call.data["correlation_id"]
        
        if correlation_id in hass.data[RESPONSE_STORE]:
            result = hass.data[RESPONSE_STORE][correlation_id]
            
            # Optionally remove from store
            if call.data.get("clear", False):
                del hass.data[RESPONSE_STORE][correlation_id]
                _LOGGER.debug("Cleared response for correlation_id: %s", correlation_id)
                
            return result
        
        _LOGGER.error("No response found for correlation_id: %s", correlation_id)
        return {"error": f"No response found for correlation_id: {correlation_id}"}
        
    return handle_get_result


async def _execute_aws_method(
    hass: HomeAssistant,
    method: Callable,
    params: Dict[str, Any],
    client_name: str,
    method_name: str,
    correlation_id: str,
    sync: bool,
) -> None:
    """Execute an AWS API method and handle the response."""
    try:
        # Execute the AWS API call in an executor
        result = await hass.async_add_executor_job(lambda: method(**params))
        _LOGGER.debug("AWS response for %s.%s: %s", client_name, method_name, result)
        
        # Store successful response
        _store_response(
            hass=hass, 
            correlation_id=correlation_id, 
            client_name=client_name, 
            method_name=method_name, 
            result=result
        )
        
        # Fire event if sync mode is enabled
        if sync:
            event_data = {
                "client": client_name,
                "method": method_name,
                "correlation_id": correlation_id, 
                "response": result
            }
            _schedule_event(hass, EVENT_BOTO3_RESPONSE, event_data)
        
    except Exception as exec_error:
        # Handle executor job errors
        _handle_error(
            hass=hass,
            error=exec_error,
            client_name=client_name,
            method_name=method_name,
            correlation_id=correlation_id,
            sync=sync
        )


def _handle_error(
    hass: HomeAssistant,
    error: Exception,
    client_name: str,
    method_name: str,
    correlation_id: str,
    sync: bool,
) -> None:
    """Handle and report an error from an AWS API call."""
    _LOGGER.error(
        "Error executing %s.%s: %s", 
        client_name, 
        method_name, 
        str(error), 
        exc_info=True
    )
    
    error_str = str(error)
    
    # Store error response
    _store_response(
        hass=hass, 
        correlation_id=correlation_id, 
        client_name=client_name, 
        method_name=method_name, 
        error=error_str
    )
    
    # Fire error event if sync mode is enabled
    if sync:
        error_event_data = {
            "client": client_name,
            "method": method_name,
            "correlation_id": correlation_id,
            "has_error": True,
            "error": error_str
        }
        _schedule_event(hass, EVENT_BOTO3_RESPONSE, error_event_data)


def _store_response(
    hass: HomeAssistant, 
    correlation_id: str, 
    client_name: str, 
    method_name: str, 
    result: Optional[Any] = None, 
    error: Optional[str] = None
) -> None:
    """Store AWS API response or error in the response store."""
    if error:
        data = {
            "client": client_name,
            "method": method_name,
            "error": error,
            "correlation_id": correlation_id
        }
    else:
        data = {
            "client": client_name,
            "method": method_name,
            "response": result,
            "correlation_id": correlation_id
        }
    
    hass.data[RESPONSE_STORE][correlation_id] = data


@callback
def _schedule_event(hass: HomeAssistant, event_name: str, event_data: Dict[str, Any]) -> None:
    """Schedule an event to be fired after a small delay."""
    hass.loop.call_later(0.1, lambda: hass.bus.async_fire(event_name, event_data)) 