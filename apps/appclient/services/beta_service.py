from typing import Any, Generic, TypeVar
from pydantic import BaseModel

from apps.appclient.services.appclient_service import AppClientService, Apps
from core.utils.request import REQUEST_METHOD, HTTPRepository

T = TypeVar("T")


class BaseBetaResponse(BaseModel, Generic[T]):
    message: str
    data: T


class BetaService:
    appClientService = AppClientService()

    def __init__(self) -> None:
        client_data = None
        try:
            client_data = self.appClientService.get_client_by_name(Apps.Beta)
        except Exception as e:
            print(e)
        self.base_url = client_data.appUrl if client_data else None
        self.httpRepository = HTTPRepository(self.base_url)

    async def interact_on_solend(self, action: str, payload: Any) -> str:
        payload["action"] = action
        res = await self.httpRepository.call(
            REQUEST_METHOD.POST, "/solend", BaseBetaResponse[str], payload
        )
        return res.data
