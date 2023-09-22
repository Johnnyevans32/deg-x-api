from typing import Optional

from pydantic import BaseModel


from apps.user.interfaces.user_interface import UserBase
from apps.wallet.interfaces.wallet_interface import WalletOut
from core.utils.aes import EncryptedDTO


class AuthResponse(BaseModel):
    user: Optional[UserBase] = None
    accessToken: Optional[str] = None
    refreshToken: Optional[str] = None
    seed: EncryptedDTO | None = None
    wallet: Optional[WalletOut] = None
