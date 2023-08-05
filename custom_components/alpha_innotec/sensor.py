import logging

from .entity import AlphaBaseEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Config entry example."""
    # assuming API object stored here by __init__.py
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    # await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        AlphaThermostatBattery(coordinator, room)
        for idx, room in enumerate(coordinator.data["rooms"])
    )


class AlphaThermostatBattery(AlphaBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = "%"
    _attr_suggested_display_precision = 0.1

    def __init__(self, coordinator, room) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, room=room)
        self._attr_unique_id = room + "_battery"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["rooms"][self.room]["battery"]
        self.async_write_ha_state()
