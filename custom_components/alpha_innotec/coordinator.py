from homeassistant.core import HomeAssistant, callback
import logging

import async_timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
from datetime import timedelta


class AlphaCoordinator(DataUpdateCoordinator):
    """Alpha Innotec Coordinator."""

    def __init__(self, hass: HomeAssistant, alpha_api, pump_api) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="AlphaSensor",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=10),
        )
        self.alpha_api = alpha_api
        self.pump_api = pump_api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                # Grab active context variables to limit data required to be fetched from API
                # Note: using context is not required if there is no need or ability to limit
                # data retrieved from API.
                data = await self.hass.async_add_executor_job(self.alpha_api.fetch_data)
                await self.hass.async_add_executor_job(self.pump_api.refresh)
                data["pump_data"] = self.pump_api.values
                return data
        except:
            pass
