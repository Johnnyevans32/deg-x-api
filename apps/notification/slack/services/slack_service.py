import json
from typing import Any

import requests

from core.config import settings
from core.utils.loggly import logger


class SlackService:
    def send_message(self, text: str, channel: str, attachments: Any = None) -> None:
        try:
            body = {"text": text, "channel": channel, "username": "lexi"}

            if attachments is not None:
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
