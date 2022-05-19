from typing import Optional

from pydantic import BaseModel

from apps.user.interfaces.user_interface import UserOut


class AuthResponse(BaseModel):
    user: UserOut
    accessToken: Optional[str]
    refreshToken: Optional[str]

    class Config:
        arbitrary_types_allowed = True
