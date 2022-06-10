from enum import Enum
from typing import Union
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.defi.interfaces.defi_provider_interface import DefiProvider
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from core.depends.get_object_id import PyObjectId
from core.depends.model import SBaseModel


class LendingRequestStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    FAILED = "failed"


class LendingRequestType(str, Enum):
    DEPOSIT = "deposit"
    BORROW = "borrow"


class InterestRateMode(str, Enum):
    STABLE = "stable"
    VARIABLE = "variable"


class LendingRequest(SBaseModel):
    user: Union[PyObjectId, User]
    wallet: Union[PyObjectId, Wallet]
    defiProvider: Union[PyObjectId, DefiProvider]
    status: LendingRequestStatus
    tokenAsset: Union[PyObjectId, TokenAsset, str]
    amount: float
    repaidAmount: float
    requestType: LendingRequestType
    interestRateMode: InterestRateMode
    # requestBeneficiary: str

    # dollarRate: float
