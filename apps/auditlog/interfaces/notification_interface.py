from enum import Enum
from typing import Union


from apps.user.interfaces.user_interface import User, UserBase

from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class NotificationType(str, Enum):
    Generic = "generic"
    WalletTX = "wallettransaction"
    DefiTX = "defitransaction"


class NotificationOut(SBaseOutModel):
    title: str
    message: str
    type: NotificationType
    user: Union[PyObjectId, UserBase, None]


class Notification(NotificationOut, SBaseModel):
    user: Union[PyObjectId, User, None]
