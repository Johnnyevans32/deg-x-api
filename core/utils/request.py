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

    def __init__(self, base_url: Optional[str] = None, headers: Any = None) -> None:
        self.base_url = base_url
        self.headers = headers
        self.session = requests.Session()
        # self.http_method = {"POST": self.session.post, "GET": self.session.get}

    async def call(
        self,
        method: REQUEST_METHOD,
        url: str,
        generic_class: Type[T],
        data: Any = None,
        opts: Any = None,
    ) -> T:
        try:

            # req.add_header('User-agent', PYCOIN_AGENT)
            url = self.base_url + url if self.base_url else url
            # req: requests.Response = self.http_method[method](url, data)
            req: requests.Response = self.session.request(
                method,
                url,
                data=data,
                headers=self.headers,
            )
            req.raise_for_status()
            if type(req.json()) is list:
                return generic_class(**{"data": req.json(), "message": "success"})
            return generic_class(**req.json())
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request call - {str(e)}")
            self.slackService.send_formatted_message(
                "HTTP request error alert!!",
                f"An error just occured \n *Error*: ```{e}``` \n *Payload:* ```{data}```",
                "error-report",
            )
            raise Exception("A request error has occured")
        except Exception as e:
            logger.error(f"Error making request call - {str(e)}")
            self.slackService.send_formatted_message(
                "HTTP request error alert!!",
                f"An error just occured \n *Error*: ```{e}``` \n *Payload:* ```{data}```",
                "error-report",
            )
            raise Exception("A request error has occured")
