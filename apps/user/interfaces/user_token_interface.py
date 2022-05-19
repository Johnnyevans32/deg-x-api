from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class UserRefreshToken(SBaseModel):
    user: PyObjectId
    refreshToken: str
