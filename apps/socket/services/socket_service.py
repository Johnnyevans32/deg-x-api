from enum import Enum
from typing import Any

import socketio

from apps.user.services.user_service import UserService

# from core.depends.get_object_id import PyObjectId

userService = UserService()
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:3000"],
    logger=True,
    engineio_logger=True,
)


class SocketEvent(str, Enum):
    NOTIFICATION = "notification"
    TRANSACTION = "transaction"


async def emit_event_to_clients(
    event: SocketEvent, data: Any, user_id: str = None
) -> None:

    return await sio.emit(event.value, data, to=user_id)


@sio.on("join")
async def handle_user_join_room(sid: str, *args: Any, **kwargs: Any) -> None:
    user_id, *_ = args
    sio.enter_room(sid, user_id)
    await sio.emit("room_joined", f"Welcome to the special room {user_id}", to=user_id)


@sio.on("connect")
async def connect(sid: str, env: Any) -> None:

    await sio.emit(
        "welcome", "Welcome to Deg X, We will have a bot attend spy on you", to=sid
    )
    # user_id = PyObjectId(env["QUERY_STRING"].split("&")[0].split("=")[1])
    # print("user_id", user_id)
    # await userService.update_user_socket_id(user_id, sid, "connect")


@sio.on("disconnect")
async def disconnect(sid: str) -> None:
    await sio.emit(
        "bye", "Goodbye to Deg X, We will have a bot attend spy on you", to=sid
    )
    # user_id = PyObjectId(env["QUERY_STRING"].split("&")[0].split("=")[1])
    # await userService.update_user_socket_id(user_id, sid, "disconnect")
