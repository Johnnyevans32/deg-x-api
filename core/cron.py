import pendulum
import openai
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
            self.sendToBROs, "interval", minutes=180
        )
        self.notify_quotes_for_bros = self.scheduler.add_job(
            self.sendQuoteToBROs, "interval", minutes=60
        )

    def sendToBROs(self) -> None:
        birthdays: dict[str, list[str]] = {
            "05-28": ["evans"],
            "05-29": ["diuto"],
            "10-19": ["geerad"],
            "10-14": ["bishop"],
            "07-03": ["godswill"],
            "06-16": ["samswift"],
        }
        todays_date = pendulum.now().format("MM-DD")

        message = "NO BIRTHDAYS TODAY, GO FUCK URSELVES YALL \npoweredby @degx"
        if not birthdays.get(todays_date):
            Utils.sendMessageToBros(message)
            return
        for name in birthdays[todays_date]:
            message = f"happy birthday {name}🥳!!! \ngo suck some dick king 😘 \npoweredby @degx"
            Utils.sendMessageToBros(message)

    def sendQuoteToBROs(self) -> None:
        message = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "whats a random mind blowing thing you have heard in any of these faucets  of our lives also selected randomly, quantum, tech, programming, universe, financial advice, travelling, world exploration, conspiracy theory, software engineering",
                }
            ],
        )
        print(message)
        Utils.sendMessageToBros(message)
