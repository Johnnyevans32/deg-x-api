import asyncio
from enum import Enum
from typing import Any, Optional, Type, TypeVar
import requests

from core.utils.loggly import logger


class REQUEST_METHOD(str, Enum):
    POST = "POST"
    GET = "GET"


class HTTPRepository:
    T = TypeVar("T")

    def __init__(self, base_url: Optional[str] = None, headers: Any = None) -> None:
        self.base_url = base_url
        self.headers = headers
        self.session = requests.Session()

    async def call(
        self,
        method: REQUEST_METHOD,
        url: str,
        generic_class: Type[T],
        data: Any | None = None,
        opts: Any | None = None,
    ) -> T:
        try:
            url = self.base_url + url if self.base_url else url

            def run_req() -> requests.Response:
                req: requests.Response = self.session.request(
                    method.name,
                    url,
                    data=data,
                    headers=self.headers,
                )
                req.raise_for_status()
                return req

            loop = asyncio.get_event_loop()
            req = await loop.run_in_executor(None, run_req)

            if type(req.json()) is list:
                return generic_class(**{"data": req.json(), "message": "success"})
            return generic_class(**req.json())
        except Exception as e:
            logger.error(f"Error making request call - {str(e)}")
            raise Exception(str(e))
