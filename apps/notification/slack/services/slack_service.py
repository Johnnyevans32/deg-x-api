import json
from typing import Any

import requests

from core.config import settings
from core.utils.loggly import logger


class SlackService:
    def send_formatted_message(
        self,
        title: str,
        msg: str,
        channel: str = "error-report",
        attachments: Any = None,
    ) -> None:
        self.send_message(f">*{title}* \n {msg}", channel, attachments)

    def send_message(
        self, text: str, channel: str = "error-report", attachments: Any = None
    ) -> None:
        try:
            assert settings.SLACKING_ENABLED, "slacking is disabled"
            body = {"text": text, "channel": channel, "username": "lexi"}

            if attachments:
                body["attachments"] = attachments

            requests.post(settings.SLACK_HOOK, data=json.dumps(body))
        except Exception as e:
            logger.info(f"Error sending message to slack - {e}")

    def notify_slack_of_demigod(self) -> None:
        text = (
            ">*🪐 Demigod Reminder 🪐* \n `This is just a daily bot "
            "reminder that my baby Evans is a fuckin god!!!`"
        )

        self.send_message(text, "general")
