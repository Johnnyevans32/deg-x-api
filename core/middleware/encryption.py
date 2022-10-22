# import json
import json
from typing import Any, Callable, Coroutine, Awaitable
from fastapi import Request, Response
from fastapi.routing import APIRoute

from starlette.middleware.base import BaseHTTPMiddleware

from starlette.types import Message, ASGIApp

from core.utils.aes import AesEncryptionService, EncryptedDTO


class DecrptRequestBody(Request):
    aesEncryptionService = AesEncryptionService()

    async def body(self) -> bytes:

        if not hasattr(self, "_body"):
            body = await super().body()
            if "encrypted" in self.headers.getlist("Content-Encoding"):
                dec_body = self.aesEncryptionService.decrypt_AES_GCM(
                    EncryptedDTO(**json.loads(body.decode()))
                )
                body = json.dumps(dec_body).encode()

            self._body = body
        return self._body


class DecrptRequestRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = DecrptRequestBody(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


class DecryptRequestMiddleware(BaseHTTPMiddleware):
    # BRUHHH SHII STILL NOT WORKING, Under construction!!!
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def set_body(self, request: Request) -> None:
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(  # type: ignore
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not hasattr(request, "_body"):
            await self.set_body(request)
            body = await request.body()
            if "encrypted" in request.headers.getlist("Content-Encoding"):
                # TODO: decrypt payload and pass as body for app usage
                body = json.dumps(
                    {
                        "fileName": "bitchhhhh",
                        "data": "bitchhhhh",
                        "auth_token": "bitchhhhh",
                        "cloudProvider": "google_service",
                    }
                ).encode("utf-8")

            request._body = body
        response = await call_next(request)
        return response
