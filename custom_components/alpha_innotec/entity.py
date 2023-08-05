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
            name=self.room + " Thermostat",
            manufacturer="Danfoss",
            model="DRS21",
        )
