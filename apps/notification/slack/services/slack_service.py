import json
from typing import Any


from core.config import settings
from core.utils.loggly import logger
from core.utils.request import REQUEST_METHOD, HTTPRepository


class SlackService:
    httpRepository = HTTPRepository()

    async def send_formatted_message(
        self,
        title: str,
        msg: str,
        channel: str = "error-report",
        attachments: Any = None,
    ) -> None:
        await self.send_message(f">*{title}* \n {msg}", channel, attachments)

    async def send_message(
        self, text: str, channel: str = "error-report", attachments: Any = None
    ) -> None:
        try:
            assert settings.SLACKING_ENABLED, "slacking is disabled"
            body = {"text": text, "channel": channel, "username": "lexi"}

            if attachments:
                body["attachments"] = attachments

            await self.httpRepository.call(
                REQUEST_METHOD.POST,
                settings.SLACK_HOOK,
                list[Any],
                json.dumps(body),
            )
        except Exception as e:
            logger.info(f"Error sending message to slack - {e}")

    async def notify_slack_of_demigod(self) -> None:
        text = (
            ">*🪐 Demigod Reminder 🪐* \n `This is just a daily bot "
            "reminder that my baby Evans is a fuckin god!!!`"
        )

        await self.send_message(text, "general")
