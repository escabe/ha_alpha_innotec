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
        AlphaThermostat(coordinator, room) for room in coordinator.data["rooms"]
    )


class AlphaThermostat(AlphaBaseEntity, ClimateEntity):
    _attr_precision = 0.1
    _attr_hvac_modes = [HVACMode.AUTO]
    _attr_hvac_mode = HVACMode.AUTO
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, coordinator, room) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, room=room)
        self._attr_unique_id = room

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_target_temperature = self.coordinator.data["rooms"][self.room][
            "controller_data"
        ]["desiredTemperature"]
        self._attr_current_temperature = self.coordinator.data["rooms"][self.room][
            "gateway_data"
        ]["currentTemperature"]
        self.async_write_ha_state()
