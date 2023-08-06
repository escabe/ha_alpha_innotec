from datetime import timedelta
import logging
from .entity import AlphaBaseEntity
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
            if module_data["type"] == "sense_control":
                li.append(
                    AlphaThermostat(
                        coordinator,
                        room=room_data["name"],
                        room_id=room_id.zfill(3),
                        thermostat_id=module_id,
                    )
                )
    async_add_entities(li)


class AlphaThermostat(AlphaBaseEntity, ClimateEntity):
    _attr_precision = 0.1
    _attr_hvac_modes = [HVACMode.AUTO]
    _attr_hvac_mode = HVACMode.AUTO
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, coordinator, room, room_id, thermostat_id) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, room=room)
        self._attr_name = room
        self.room_id = room_id
        self.thermostat_id = thermostat_id
        self._attr_unique_id = "room_" + room_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_target_temperature = self.coordinator.data["rooms"][self.room_id][
            "desiredTemperature"
        ]
        self._attr_current_temperature = self.coordinator.data["modules"][
            self.thermostat_id
        ]["currentTemperature"]
        self.async_write_ha_state()
