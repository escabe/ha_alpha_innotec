import logging

from .entity import AlphaBaseEntity, AlphaPumpBaseEntity
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
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    allmodules = hass.data[DOMAIN][entry.entry_id]["allmodules"]
    pumpmap = hass.data[DOMAIN][entry.entry_id]["pumpmap"]

    pump_name = coordinator.data["sysinfo"]["operationModeLabel"]
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
                    AlphaThermostatBattery(
                        coordinator, room=room_data["name"], module_id=module_id
                    )
                )
    for cat, items in pumpmap.items():
        for name, id in items.items():
            if cat == "Temperaturen":
                li.append(AlphaPumpTemperature(coordinator, pump_name, name, id))
            elif cat == "Energie":
                li.append(AlphaPumpEnergy(coordinator, pump_name, name, id))
            elif cat == "Installatiestatus" and name == "Vermogen":
                li.append(AlphaPumpPower(coordinator, pump_name, name, id))
            elif cat == "Ingangen" and name == "Debiet":
                li.append(
                    AlphaPumpFlow(coordinator, pump_name, "Waterdoorstroming", id)
                )

    li.append(AlphaPumpMode(coordinator, pump_name, "Mode", None))

    async_add_entities(li)


class AlphaThermostatBattery(AlphaBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = "%"
    _attr_suggested_display_precision = 0.1

    def __init__(self, coordinator, room, module_id) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, room=room)
        self._attr_name = "Battery"
        self.module_id = module_id
        self._attr_unique_id = module_id + "_battery"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["modules"][self.module_id][
            "battery"
        ]
        self.async_write_ha_state()


class AlphaPumpTemperature(AlphaPumpBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = "°C"
    _attr_suggested_display_precision = 0.1

    def __init__(self, coordinator, pump_name, name, id) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, pump_name, name, id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        val = self.coordinator.data["pump_data"][self.id]

        if "°C" in val:
            self._attr_native_unit_of_measurement = "°C"
            self._attr_native_value = float(val.strip("°C"))
        elif "K" in val:
            self._attr_native_unit_of_measurement = "K"
            self._attr_native_value = float(val.strip("K"))

        self.async_write_ha_state()


class AlphaPumpEnergy(AlphaPumpBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = "kWh"
    _attr_suggested_display_precision = 0.1
    _attr_state_class = "total_increasing"

    def __init__(self, coordinator, pump_name, name, id) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, pump_name, name, id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        val = self.coordinator.data["pump_data"][self.id]

        if "kWh" in val:
            self._attr_native_unit_of_measurement = "kWh"
            self._attr_native_value = float(val.strip("kWh"))

        self.async_write_ha_state()


class AlphaPumpPower(AlphaPumpBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = "kW"
    _attr_suggested_display_precision = 0.1

    def __init__(self, coordinator, pump_name, name, id) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, pump_name, name, id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        val = self.coordinator.data["pump_data"][self.id]

        if "kW" in val:
            self._attr_native_unit_of_measurement = "kW"
            self._attr_native_value = float(val.strip("kW"))

        self.async_write_ha_state()


class AlphaPumpFlow(AlphaPumpBaseEntity, SensorEntity):
    _attr_device_class = None
    _attr_native_unit_of_measurement = "l/h"
    _attr_suggested_display_precision = 0.1

    def __init__(self, coordinator, pump_name, name, id) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, pump_name, name, id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        val = self.coordinator.data["pump_data"][self.id]

        if "l/h" in val:
            self._attr_native_unit_of_measurement = "l/h"
            val = val.strip(" l/h")
            if val == "---":
                self._attr_native_value = 0.0
            else:
                self._attr_native_value = float(val) / 60.0

        self.async_write_ha_state()


class AlphaPumpMode(AlphaPumpBaseEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["standby", "heating mode", "cooling mode", "hot water"]

    def __init__(self, coordinator, pump_name, name, id) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, pump_name, name, id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        val = self.coordinator.data["sysinfo"]["operationMode"]
        self._attr_native_value = val.strip()

        self.async_write_ha_state()
