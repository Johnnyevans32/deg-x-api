from typing import Optional

from pydantic import BaseModel

from apps.user.interfaces.user_interface import UserBase
from apps.wallet.interfaces.wallet_interface import WalletOut
from core.utils.aes import EncryptedDTO


class AuthResponse(BaseModel):
    user: Optional[UserBase]
    accessToken: Optional[str]
    refreshToken: Optional[str]
    seed: Optional[EncryptedDTO]
    wallet: Optional[WalletOut]

    class Config:
        arbitrary_types_allowed = True
