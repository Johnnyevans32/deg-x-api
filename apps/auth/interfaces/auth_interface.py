from typing import Optional

from pydantic import BaseModel

from apps.user.interfaces.user_interface import UserBase
from apps.wallet.interfaces.wallet_interface import WalletOut
from core.utils.aes import KeystoreModel


class AuthResponse(BaseModel):
    user: Optional[UserBase]
    accessToken: Optional[str]
    refreshToken: Optional[str]
    keystore: Optional[KeystoreModel]
    wallet: Optional[WalletOut]

    class Config:
        arbitrary_types_allowed = True
