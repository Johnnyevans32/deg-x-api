from typing import Optional
from pydantic import BaseModel

from apps.user.interfaces.user_interface import UserBase
from core.utils.aes import KeystoreModel


class AuthResponse(BaseModel):
    user: Optional[UserBase]
    accessToken: Optional[str]
    refreshToken: Optional[str]
    keystore: Optional[KeystoreModel]

    class Config:
        arbitrary_types_allowed = True
