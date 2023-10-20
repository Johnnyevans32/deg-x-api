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
        birthdays: dict[str, list[dict[str, str]]] = {
            "10-20": [{"name": "evans", "pn": "2349061349498"}],
            "11-16": [{"name": "david", "pn": "2349061349498"}],
            "05-24": [{"name": "hans", "pn": "2349061349498"}],
            "05-29": [{"name": "diuto", "pn": "2349061349498"}],
            "10-19": [{"name": "geerad", "pn": "2349061349498"}],
            "10-14": [{"name": "bishop", "pn": "2349061349498"}],
            "07-03": [{"name": "godswill", "pn": "2349061349498"}],
            "06-16": [{"name": "samswift", "pn": "2349061349498"}],
            "08-30": [{"name": "sammy", "pn": "2349061349498"}],
            "12-08": [{"name": "noel", "pn": "2349061349498"}],
        }
        todays_date = pendulum.now().format("MM-DD")

        if not birthdays.get(todays_date):
            return
        for bro in birthdays[todays_date]:
            message = (
                f"it is @{bro['pn']} birthday today yall! \nhappy birthday "
                f"{bro['name']}🥳!!! \ngo suck some dick king 😘 \npowered by BROs"
            )
            Utils.sendMessageToBros(message, bro["pn"])

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
                "nigeria history",
                "introduction to computer age",
                "love",
                "religion",
                "astrophysics",
                "black hole",
            ]
            response = g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                # provider=g4f.Provider.Aichat,
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
