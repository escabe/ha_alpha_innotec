import logging

from .entity import AlphaBaseEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Config entry example."""
    # assuming API object stored here by __init__.py
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    allmodules = hass.data[DOMAIN][entry.entry_id]["allmodules"]
    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    # await coordinator.async_config_entry_first_refresh()
    li = []
    for room_id, room_data in allmodules["modules"]["rooms"].items():
        for module_id, module_data in room_data["modules"].items():
            if module_data["type"] == "floor":
                li.append(
                    AlphaFloorUnit(
                        coordinator,
                        room=room_data["name"],
                        module_id=module_id,
                        instance=module_data["moduleInstance"],
                    )
                )

    async_add_entities(li)


class AlphaFloorUnit(AlphaBaseEntity, BinarySensorEntity):
    _attr_device_class = None

    def __init__(self, coordinator, room, module_id, instance) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, room=room)
        self._attr_unique_id = module_id + "_valve"
        self._attr_name = "Valve"
        self.module_id = "00" + module_id[2:]
        self.instance = instance

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        for data in self.coordinator.data["modules"][self.module_id]["instances"]:
            if data["instance"] == self.instance:
                self._attr_is_on = data["status"]
                self.async_write_ha_state()
                return
