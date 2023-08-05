import hashlib
import base64
import requests
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


class AlphaAPI:
    def __init__(
        self,
        controlbox_ip: str,
        controlbox_username: str,
        controlbox_password: str,
        gateway_password: str,
    ) -> None:
        self.controlbox_ip = controlbox_ip
        self.controlbox_username = controlbox_username
        self.controlbox_password = controlbox_password
        self.gateway_password = gateway_password

    @staticmethod
    def stringToCharcodes(s: str) -> str:
        return "".join([str(ord(c)).zfill(3) for c in s])

    @staticmethod
    def getRequestSignature(params: dict, key: str) -> str:
        signature = (
            "|".join([k + "=" + str(v) for k, v in sorted(params.items())]) + "|"
        )
        signature = AlphaAPI.stringToCharcodes(signature)
        key = AlphaAPI.stringToCharcodes(key)
        b = hashlib.pbkdf2_hmac("sha512", signature.encode(), key.encode(), 1)
        return base64.b64encode(b)

    @staticmethod
    def decrypt(encrypted_data: str, key: str):
        static_iv = "D3GC5NQEFH13is04KD2tOg=="
        crypt_key = SHA256.new(key.encode())
        crypt_key = crypt_key.digest()
        cipher = AES.new(crypt_key, AES.MODE_CBC, base64.b64decode(static_iv))
        return (
            cipher.decrypt(base64.b64decode(encrypted_data))
            .decode("ascii")
            .strip("\x10")
        )

    def login(self) -> bool:
        res = requests.post(
            f"http://{self.controlbox_ip}/api/user/token/challenge",
            data={"udid": "HomeAssistant"},
        )
        data = res.json()
        if not data["success"]:
            raise data["message"]
        self.device_token = data["devicetoken"]

        res = requests.post(
            f"http://{self.controlbox_ip}/api/user/token/response",
            data={
                "udid": "HomeAssistant",
                "login": self.controlbox_username,
                "token": self.device_token,
                "hashed": base64.b64encode(
                    hashlib.pbkdf2_hmac(
                        "sha512",
                        AlphaAPI.stringToCharcodes(self.controlbox_password).encode(),
                        AlphaAPI.stringToCharcodes(self.device_token).encode(),
                        1,
                    )
                ),
            },
        )
        data = res.json()
        if not data["success"]:
            raise data["message"]
        self.controlbox_devicetoken_encrypted = data["devicetoken_encrypted"]
        self.controlbox_devicetoken = AlphaAPI.decrypt(
            self.controlbox_devicetoken_encrypted, self.controlbox_password
        )
        self.controlbox_userid = data["userid"]
        self.controlbox_reqcount = 0

        data = self.doRequest("gateway/configuration/get")
        self.gateway_ip = data["gateway"]["address"]

        return True

    def doRequest(self, endpoint: str, data: dict = None) -> dict:
        if data is None:
            data = dict()
        data["reqcount"] = self.controlbox_reqcount
        data["udid"] = "HomeAssistant"
        data["userid"] = self.controlbox_userid
        data["request_signature"] = AlphaAPI.getRequestSignature(
            data, self.controlbox_devicetoken
        )
        res = requests.post(f"http://{self.controlbox_ip}/api/{endpoint}", data=data)
        data = res.json()
        if not data["success"]:
            raise data["message"]
        self.controlbox_reqcount += 1
        return data

    def gatewayRequest(self, endpoint: str, data: dict = None) -> dict:
        if data is None:
            data = dict()
        data["udid"] = "HomeAssistant"
        data["userlogin"] = "gateway"
        data["request_signature"] = AlphaAPI.getRequestSignature(
            data, self.gateway_password
        )
        res = requests.post(f"http://{self.gateway_ip}/api/{endpoint}", data=data)
        data = res.json()
        if not data["success"]:
            raise data["message"]
        self.controlbox_reqcount += 1
        return data

    def fetch_data(self):
        rooms = {}
        floors = {}
        roomdata = self.doRequest("room/list")
        gatewaydata = self.gatewayRequest("gateway/dbmodules")
        sysinfo = self.doRequest("systeminformation")
        for g in roomdata["groups"]:
            for r in g["rooms"]:
                rooms[r["name"]] = {"controller_data": r}
        for id, m in gatewaydata["modules"].items():
            if m["type"] == "sense_control":
                rooms[m["room"]]["gateway_data"] = m
            elif m["type"] == "floor":
                floors[m["name"]] = m
        return {"rooms": rooms, "sysinfo": sysinfo, "floors": floors}
