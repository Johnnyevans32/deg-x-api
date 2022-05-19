from typing import Any

import requests

from core.utils.loggly import logger


class TelegramService:
    def send_message(self, msg: str) -> Any:
        try:
            api_key = "5317063199:AAF0Q0nd7fB5o_g5sm8i7kmw_d7TKmPmwHU"
            user_id = "alien_corp"

            telegram_api_url = f"""https://api.telegram.org/bot{api_key}/
                                sendMessage?chat_id=@{user_id}&text={msg}&parse_mode=markdown"""
            tel_resp = requests.get(telegram_api_url)
            return tel_resp

        except Exception as e:
            logger.info(f"Error sending message to slack - {e}")

    def update_buy_action(self, amount: int):
        pass
