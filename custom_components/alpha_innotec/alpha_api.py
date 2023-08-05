import random


class AlphaAPI:
    def __init__(
        self,
        host: str,
        contoller_username: str,
        controller_password: str,
        gateway_password: str,
    ) -> None:
        self.host = host
        self.contoller_username = contoller_username
        self.controller_password = controller_password
        self.gateway_password = gateway_password

    async def login(self) -> bool:
        """Test if we can authenticate with the host."""
        return True

    async def fetch_data(self):
        return {
            "rooms": {
                "roomA": {
                    "target_temp": random.random(),
                    "current_temp": random.random(),
                    "battery": random.random() * 100,
                },
                "roomB": {
                    "target_temp": random.random(),
                    "current_temp": random.random(),
                    "battery": random.random() * 100,
                },
            }
        }
