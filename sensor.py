"""Sensor platform for Akahu."""
import asyncio
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_HOST

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=15)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Akahu sensors from a config entry."""
    session = async_get_clientsession(hass)
    headers = {
        "Authorization": f"Bearer {entry.data[CONF_TOKEN]}",
        "X-Akahu-ID": entry.data["app_token"],
    }

    async def async_update_data():
        """Fetch data from Akahu API."""
        try:
            async with asyncio.timeout(10):
                async with session.get(f"{API_HOST}/accounts", headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    # We key the data by account ID for easy lookup
                    return {item["_id"]: item for item in data.get("items", [])}
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Akahu API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="akahu_sensor",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    # Fetch initial data so we have it when we create entities
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        AkahuAccountSensor(coordinator, account_id)
        for account_id in coordinator.data.keys()
    )

class AkahuAccountSensor(SensorEntity):
    """Representation of an Akahu account balance sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, account_id: str) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._account_id = account_id
        
        # Initial data from the coordinator
        account_data = self.coordinator.data[self._account_id]
        connection_name = account_data.get("connection", {}).get("name", "Unknown")
        
        self._attr_name = f"{connection_name} {account_data['name']}"
        self._attr_unique_id = self._account_id
        self._attr_icon = "mdi:bank"
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_native_unit_of_measurement = account_data.get("balance", {}).get("currency")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor (the account balance)."""
        return self.coordinator.data[self._account_id].get("balance", {}).get("current")

    @property
    def extra_state_attributes(self) -> dict:
        """Return other details as sensor attributes."""
        account_data = self.coordinator.data[self._account_id]
        return {
            "account_type": account_data.get("type"),
            "available_balance": account_data.get("balance", {}).get("available"),
            "institution": account_data.get("connection", {}).get("name"),
            "akahuID": account_data.get("_id"),
            "status": account_data.get("status"),
            "formatted_account_number": account_data.get("formatted_account"),
        }
        
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )