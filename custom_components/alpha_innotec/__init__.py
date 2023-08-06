"""The Alpha Innotec Heating and Cooling integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

from .alpha_api import AlphaAPI

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR, Platform.BINARY_SENSOR]
from .coordinator import AlphaCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alpha Innotec Heating and Cooling from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    alpha_api = AlphaAPI(
        entry.data["controller_host"],
        entry.data["controller_username"],
        entry.data["controller_password"],
        entry.data["gateway_password"],
    )
    success = await hass.async_add_executor_job(alpha_api.login)
    allmodules = await hass.async_add_executor_job(
        alpha_api.gatewayRequest, "gateway/allmodules"
    )
    coordinator = AlphaCoordinator(hass, alpha_api)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "allmodules": allmodules,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
