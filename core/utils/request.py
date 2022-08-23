from enum import Enum
from typing import Any, Optional, Type, TypeVar

import requests

from apps.notification.slack.services.slack_service import SlackService
from core.utils.loggly import logger


class REQUEST_METHOD(str, Enum):
    POST = "POST"
    GET = "GET"


class HTTPRepository:
    slackService = SlackService()
    T = TypeVar("T")

    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = base_url
        self.session = requests.Session()
        # self.http_method = {"POST": self.session.post, "GET": self.session.get}

    async def call(
        self,
        method: REQUEST_METHOD,
        url: str,
        generic_class: Type[T],
        data: Any = None,
        opts: Any = None,
    ):
        try:

            # req.add_header('User-agent', PYCOIN_AGENT)
            url = self.base_url + url if self.base_url else url
            # req: requests.Response = self.http_method[method](url, data)
            req: requests.Response = self.session.request(
                method, url, data=data, **opts
            )
            req.raise_for_status()
            return generic_class(**req.json())  # type: ignore [call-arg]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request call - {str(e)}")
            self.slackService.send_formatted_message(
                "HTTP request error alert!!",
                f"An error just occured \n *Error*: ```{e}``` \n *Payload:* ```{data}```",
                "error-report",
            )
            raise Exception("A request error has occured")
