import random
import pendulum
import g4f
import traceback
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
            self.sendToBROs, "interval", minutes=240
        )
        self.notify_quotes_for_bros = self.scheduler.add_job(
            self.sendQuoteToBROs, "interval", minutes=60
        )

    def sendToBROs(self) -> None:
        birthdays: dict[str, list[str]] = {
            "05-28": ["evans"],
            "11-16": ["david"],
            "05-24": ["hans"],
            "05-29": ["diuto"],
            "10-19": ["geerad"],
            "10-14": ["bishop"],
            "07-03": ["godswill"],
            "06-16": ["samswift"],
            "08-30": ["sammy"],
            "12-08": ["noel"],
        }
        todays_date = pendulum.now().format("MM-DD")

        if not birthdays.get(todays_date):
            return
        for name in birthdays[todays_date]:
            message = f"happy birthday {name}🥳!!! \ngo suck some dick king 😘 \npoweredby @BROs"
            Utils.sendMessageToBros(message)

    def sendQuoteToBROs(self) -> None:
        try:
            topics = [
                "quantum",
                "tech",
                "programming",
                "universe",
                "financial advice",
                "travelling",
                "world exploration",
                "conspiracy theory",
                "software engineering",
            ]
            response = g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                provider=g4f.Provider.Aichat,
                messages=[
                    {
                        "role": "user",
                        "content": "go straight to the gist by telling us a "
                        f"random mind blowing thing you have heard in {random.choice(topics)} "
                        "also please dont include link quoting AND Go STRAIGHT TO THE "
                        "POINT BY STARTING, ON A RANDOM NOTE and then the answer",
                    }
                ],
            )
            Utils.sendMessageToBros(response)
        except Exception as e:
            traceback.print_exc()
            print("this is an from quote to bros", e)
