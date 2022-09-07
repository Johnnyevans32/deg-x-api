from enum import Enum
from functools import wraps
from typing import Any, Callable

from apps.appclient.interfaces.appclient_interface import AppClient
from core.utils.custom_exceptions import UnicornException, UnicornRequest
from core.utils.model_utility_service import ModelUtilityService
from core.utils.utils_service import Utils


class Apps(str, Enum):
    Beta = "beta"


class AppClientService:
    def client_auth(self, func: Callable[[UnicornRequest, Any, Any], Any]) -> Any:
        @wraps(func)
        async def wrapper(request: UnicornRequest, *args: Any, **kwargs: Any) -> Any:
            client_id = request.headers.get("clientID")
            client_secret = request.headers.get("clientSecret")

            if not client_id or not client_secret:
                raise UnicornException(
                    status_code=403, message="incomplete client credentials specified"
                )

            app_client = await self.get_client_by_query(
                {"_id": client_id, "isDeleted": False}
            )

            if app_client.clientSecret != client_secret:
                raise UnicornException(
                    status_code=403, message="incomplete client credentials specified"
                )

            request.state.app_client = app_client
            return func(request, *args, **kwargs)

        return wrapper

    async def get_client_by_query(self, query: dict[str, Any]) -> AppClient:
        app_client = await ModelUtilityService.find_one(
            AppClient,
            query,
        )

        if not app_client:
            raise UnicornException(status_code=403, message="client not found")

        return app_client

    def get_client_by_name(self, name: str) -> AppClient:
        app_client = ModelUtilityService.non_async_find_one(
            AppClient,
            {"name": name, "isDeleted": False},
        )

        if not app_client:
            raise UnicornException(status_code=403, message="client not found")

        return app_client

    async def create_client(self, client: AppClient) -> AppClient:
        client.clientSecret = Utils.generate_random(24)
        client.clientID = Utils.generate_random(12)
        dict_client = client.dict(by_alias=True, exclude_none=True)

        client_obj = await ModelUtilityService.model_create(
            AppClient,
            dict_client,
        )

        return client_obj
