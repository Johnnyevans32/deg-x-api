from enum import Enum
from typing import Union

from pydantic import Field

from apps.blockchain.interfaces.network_interface import NetworkType
from apps.user.interfaces.user_interface import User
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel, SBaseOutModel


class WalletType(str, Enum):
    MULTICHAIN = "multichain"
    SINGLECHAIN = "singlechain"


class FiatCurrency(str, Enum):
    USD = "usd"
    NGN = "ngn"


class WalletOut(SBaseOutModel):
    name: str
    user: Union[PyObjectId, User]
    walletType: WalletType
    networkType: NetworkType = Field(default=NetworkType.TESTNET)
    fiatCurrency: FiatCurrency = Field(default=FiatCurrency.USD)
    isDefault: bool = Field(default=True)
    qrImage: str | None = None


class Wallet(WalletOut, SBaseModel):
    mnemonic: str | None = None

    # @property
    # async def assets(self) -> list[WalletAsset]:
    #     from apps.wallet.interfaces.walletasset_interface import WalletAsset

    #     walletassets = await ModelUtilityService.find(
    #         WalletAsset, {"wallet": self.id, "isDeleted": False}
    #     )

    #     return walletassets
