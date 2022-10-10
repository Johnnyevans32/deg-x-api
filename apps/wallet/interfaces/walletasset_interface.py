from typing import Union

from pydantic import BaseModel, Field

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset, TokenOut
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet, WalletOut
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class Address(BaseModel):
    main: str
    test: str


class WalletAssetOut(SBaseOutModel):
    tokenasset: Union[PyObjectId, TokenOut]
    wallet: Union[PyObjectId, WalletOut]
    address: Address
    balance: float = Field(default=0)


class WalletAsset(WalletAssetOut, SBaseModel):
    tokenasset: Union[PyObjectId, TokenAsset]
    blockchain: Union[PyObjectId, Blockchain]
    user: Union[PyObjectId, User]
    wallet: Union[PyObjectId, Wallet]
