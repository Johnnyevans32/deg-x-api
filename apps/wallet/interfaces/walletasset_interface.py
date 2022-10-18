from typing import Union

from pydantic import BaseModel, Field

from apps.blockchain.interfaces.blockchain_interface import Blockchain, BlockchainOut
from apps.blockchain.interfaces.network_interface import NetworkType
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset, TokenAssetOut
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet, WalletOut
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class Address(BaseModel):
    main: str
    test: str


class Balance(BaseModel):
    mainnet: float
    testnet: float


class WalletAssetOut(SBaseOutModel):
    tokenasset: Union[PyObjectId, TokenAssetOut]
    wallet: Union[PyObjectId, WalletOut]
    blockchain: Union[PyObjectId, BlockchainOut]
    address: str
    balance: float = Field(default=0)
    networkType: NetworkType


class WalletAsset(WalletAssetOut, SBaseModel):
    tokenasset: Union[PyObjectId, TokenAsset]
    blockchain: Union[PyObjectId, Blockchain]
    user: Union[PyObjectId, User]
    wallet: Union[PyObjectId, Wallet]
