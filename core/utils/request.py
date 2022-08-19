from typing import Any, Type, TypeVar

import requests

from apps.notification.slack.services.slack_service import SlackService
from core.utils.loggly import logger


class HTTPRepository:
    slackService = SlackService()
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
            # req.add_header('User-agent', PYCOIN_AGENT)
            req: requests.Response = self.http_method[method](url, data)
            req.raise_for_status()
            return generic_class(**req.json())  # type: ignore [call-arg]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request call - {str(e)}")
            self.slackService.send_formatted_message(
                "HTTP request error alert!!",
                f"An error just occured \n *Error*: ```{e}``` \n *Payload:* ```{req.json()}```",
                "error-report",
            )
            raise Exception("A request error has occured")
