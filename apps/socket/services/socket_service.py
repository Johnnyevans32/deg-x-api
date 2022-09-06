from typing import Any

import socketio

from apps.user.services.user_service import UserService
from core.depends.get_object_id import PyObjectId

userService = UserService()
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
)


@sio.on("leave")
async def handle_leave(sid: str, *args: Any, **kwargs: Any) -> None:
    print("handle leainggg", sid)
    print(args)
    print(kwargs)
    await sio.emit("lobby", "User left", to=sid)


@sio.on("connect")
async def connect(sid: str, env: Any) -> None:
    user_id = PyObjectId(env["QUERY_STRING"].split("&")[0].split("=")[1])
    await userService.update_user_socket_id(user_id, sid, "connect")


@sio.on("disconnect")
async def disconnect(sid: str, env: Any) -> None:
    user_id = PyObjectId(env["QUERY_STRING"].split("&")[0].split("=")[1])
    await userService.update_user_socket_id(user_id, sid, "disconnect")
