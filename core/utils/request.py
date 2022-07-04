from typing import Any, Type, TypeVar

import requests
from core.utils.loggly import logger


class HTTPRepository:
    T = TypeVar("T")
    http_method = {"POST": requests.post, "GET": requests.get}

    async def call(
        self,
        method: str,
        url: str,
        generic_class: Type[T],
        data: Any = None,
        opts: Any = None,
    ):
        try:
            req: requests.Response = self.http_method[method](url, data)
            return generic_class(**req.json())  # type: ignore [call-arg]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request call - {str(e)}")
            raise e
