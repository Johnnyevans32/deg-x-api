from typing import Optional

from pydantic import BaseModel

from apps.user.interfaces.user_interface import UserBase


class AuthResponse(BaseModel):
    user: UserBase
    accessToken: Optional[str]
    refreshToken: Optional[str]

    class Config:
        arbitrary_types_allowed = True
