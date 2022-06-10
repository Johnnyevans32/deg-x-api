from functools import wraps
from typing import Callable

from apps.appclient.interfaces.appclient_interface import AppClient, AppClientIn
from core.db import db
from core.utils.custom_exceptions import UnicornException, UnicornRequest
from core.utils.utils_service import Utils
from core.utils.model_utility_service import ModelUtilityService


class AppClientService:
    def client_auth(self, func: Callable):
        @wraps(func)
        async def wrapper(request: UnicornRequest, *args, **kwargs):
            client_id = request.headers.get("clientID")
            client_secret = request.headers.get("clientSecret")

            if client_id is None or client_secret is None:
                raise UnicornException(
                    status_code=403, message="incomplete client credentials specified"
                )

            app_client = self.get_client_by_id(client_id)

            if app_client is False or app_client.clientSecret != client_secret:
                raise UnicornException(
                    status_code=403, message="incomplete client credentials specified"
                )

            request.state.app_client = app_client
            return func(request, *args, **kwargs)

        return wrapper

    def get_client_by_id(self, client_id: str) -> AppClient:
        app_client = db.appclient.find_one({"clientID": client_id})

        if app_client is None:
            raise UnicornException(status_code=403, message="client not found")

        return AppClient(**app_client)

    def get_client_by_secret(self, client_secret: str) -> AppClient:
        app_client = db.appclient.find_one({"clientSecret": client_secret})

        if app_client is None:
            raise UnicornException(status_code=403, message="client not found")

        return AppClient(**app_client)

    def create_client(self, client: AppClientIn) -> AppClient:
        client.clientSecret = Utils.generate_random(24)
        client.clientID = Utils.generate_random(12)
        dict_client = client.dict(by_alias=True, exclude_none=True)

        client_obj = ModelUtilityService.model_create(
            AppClient,
            dict_client,
        )

        return client_obj
