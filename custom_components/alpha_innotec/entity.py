from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN


class AlphaBaseEntity(CoordinatorEntity, Entity):
    def __init__(self, coordinator, room) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=room)
        self.room = room

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.room)},
            name=self.room + " Climate",
            manufacturer="Alpha Innotec",
            model="Room",
        )


class AlphaPumpBaseEntity(CoordinatorEntity, Entity):
    def __init__(self, coordinator, pump_name, name, id) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = name
        self.id = id
        self.pump_name = pump_name

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.pump_name)},
            name=self.pump_name,
            manufacturer="Alpha Innotec",
            model=self.pump_name,
        )
