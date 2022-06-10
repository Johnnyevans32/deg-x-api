from typing import Union

from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class WalletAsset(SBaseModel):
    tokenasset: Union[PyObjectId, TokenAsset]
    user: Union[PyObjectId, User]
    wallet: Union[PyObjectId, Wallet]
    address: str
    # balance: int
