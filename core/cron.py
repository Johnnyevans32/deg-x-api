import pendulum
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.notification.slack.services.slack_service import SlackService
from core.utils.loggly import logger
from core.utils.utils_service import Utils


def test_job() -> None:
    logger.info("CRON JOB BOT HERE")


class CronJob:
    def __init__(self) -> None:
        self.slackService = SlackService()

        self.scheduler = AsyncIOScheduler()

        # self.notify_slack_for_demigod = self.scheduler.add_job(
        #     self.slackService.notify_slack_of_demigod, "interval", minutes=180
        # )
        self.notify_message_for_bros = self.scheduler.add_job(
            self.sendToBROs, "interval", minutes=60
        )

    def sendToBROs(self) -> None:
        birthdays: dict[str, list[str]] = {
            "05-28": ["evans"],
            "10-19": ["geerad"],
            "10-14": ["bishop"],
        }
        todays_date = pendulum.now().format("MM-DD")

        message = "NO BIRTHDAYS TODAY, GO FUCK URSELVES YALL"
        if not birthdays.get(todays_date):
            Utils.sendMessageToBros(message)
            return
        for name in birthdays[todays_date]:
            message = f"happy birthday {name}🥳!!! \ngo suck some dick king 😘"
            Utils.sendMessageToBros(message)
