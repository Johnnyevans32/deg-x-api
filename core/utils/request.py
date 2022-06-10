from typing import Any, Type, TypeVar

import requests


class HTTPRepository:
    T = TypeVar("T")
    http_method = {"POST": requests.post, "GET": requests.get}

    def call(
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
            raise e
