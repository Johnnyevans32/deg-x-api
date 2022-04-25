from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.notification.slack.services.slack_service import SlackService
from core.utils.loggly import logger


def test_job():
    logger.info("CRON JOB BOT HERE")


class CronJob:
    def __init__(self) -> None:
        self.slackService = SlackService()

        self.scheduler = AsyncIOScheduler()

        # self.test_job = self.scheduler.add_job(test_job, "interval", seconds=100)
        self.notify_slack_for_demigod = self.scheduler.add_job(
            self.slackService.notify_slack_of_demigod, "interval", seconds=10800
        )
