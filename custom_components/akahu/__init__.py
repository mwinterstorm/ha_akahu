"""The Akahu integration."""
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, API_HOST

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

SERVICE_TRANSFER = "transfer"
SERVICE_REFRESH = "refresh"
ATTR_FROM_ACCOUNT = "from_account"
ATTR_TO_ACCOUNT = "to_account"
ATTR_AMOUNT = "amount"

SERVICE_TRANSFER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_FROM_ACCOUNT): cv.string,
        vol.Required(ATTR_TO_ACCOUNT): cv.string,
        vol.Required(ATTR_AMOUNT): vol.Coerce(float),
    }
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Akahu from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    entry.async_on_unload(entry.add_update_listener(update_listener))

    session = async_get_clientsession(hass)
    headers = {
        "Authorization": f"Bearer {entry.data['token']}",
        "X-Akahu-ID": entry.data["app_token"],
    }

    async def async_handle_transfer(call: ServiceCall) -> None:
        """Handle the service call to initiate a transfer."""
        from_account = call.data[ATTR_FROM_ACCOUNT]
        to_account = call.data[ATTR_TO_ACCOUNT]
        amount = call.data[ATTR_AMOUNT]

        payload = {
            "to": to_account,
            "from": from_account,
            "amount": amount,
        }

        async with session.post(f"{API_HOST}/transfers", headers=headers, json=payload) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to initiate transfer: %s", await resp.text())
                return

    async def async_handle_refresh(call: ServiceCall) -> None:
        """Handle the service call to refresh the data."""
        _LOGGER.info("Requesting manual refresh from Akahu API.")
        async with session.post(f"{API_HOST}/refresh", headers=headers) as resp:
            if resp.status == 200:
                _LOGGER.info("Akahu accepted the refresh request. Now fetching updated data.")
                await hass.data[DOMAIN][entry.entry_id].async_request_refresh()
            else:
                _LOGGER.warning(
                    "Akahu refresh request failed with status %s. This may be due to the 15-minute refresh rest period.",
                    resp.status,
                )

    hass.services.async_register(
        DOMAIN, SERVICE_TRANSFER, async_handle_transfer, schema=SERVICE_TRANSFER_SCHEMA
    )
    hass.services.async_register(DOMAIN, SERVICE_REFRESH, async_handle_refresh)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload the sensor platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove the services
        hass.services.async_remove(DOMAIN, SERVICE_TRANSFER)
        hass.services.async_remove(DOMAIN, SERVICE_REFRESH)
        # Clean up the hass.data entry
        if hass.data[DOMAIN].get(entry.entry_id):
            hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)