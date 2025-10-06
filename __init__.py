# akahu/__init__.py
"""The Akahu integration."""
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv


from .const import DOMAIN, API_HOST

# List the platforms that your integration will support.
PLATFORMS = [Platform.SENSOR]

SERVICE_TRANSFER = "transfer"
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

    async def async_handle_transfer(call: ServiceCall) -> None:
        """Handle the service call to initiate a transfer."""
        from_account = call.data[ATTR_FROM_ACCOUNT]
        to_account = call.data[ATTR_TO_ACCOUNT]
        amount = call.data[ATTR_AMOUNT]

        session = async_get_clientsession(hass)
        headers = {
            "Authorization": f"Bearer {entry.data['token']}",
            "X-Akahu-ID": entry.data["app_token"],
        }
        payload = {
            "to": to_account,
            "from": from_account,
            "amount": amount,
        }

        async with session.post(f"{API_HOST}/transfers", headers=headers, json=payload) as resp:
            if resp.status != 200:
                # You might want to add more robust error handling here
                return

    hass.services.async_register(
        DOMAIN, SERVICE_TRANSFER, async_handle_transfer, schema=SERVICE_TRANSFER_SCHEMA
    )

    # This forwards the config entry to the sensor platform.
    # The sensor.py file will then use the entry to set up the sensors.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when the user removes the integration.
    hass.services.async_remove(DOMAIN, SERVICE_TRANSFER)
    return await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)