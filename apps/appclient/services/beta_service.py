from typing import Any

from pydantic import BaseModel

# from apps.appclient.interfaces.appclient_interface import AppClient
from apps.appclient.services.appclient_service import AppClientService, Apps
from core.utils.request import HTTPRepository


class BaseBetaResponse(BaseModel):
    message: str
    data: Any


class BetaService:
    appClientService = AppClientService()
    base_url: str = ""

    def __init__(self):
        client_data = None
        try:
            client_data = self.appClientService.get_client_by_name(Apps.Beta)
        except Exception as e:
            print(e)
        self.base_url = client_data.appUrl or None
        self.httpRepository = HTTPRepository(self.base_url)

    async def interact_on_solend(self, action: str, payload: Any):
        payload["action"] = action
        res = await self.httpRepository.call(
            "POST", "/solend", BaseBetaResponse, payload
        )
        return res.data
