"""The Akahu integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# List the platforms that your integration will support.
PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Akahu from a config entry."""
    # This forwards the config entry to the sensor platform.
    # The sensor.py file will then use the entry to set up the sensors.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when the user removes the integration.
    return await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)