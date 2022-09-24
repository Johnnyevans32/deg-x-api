import abc
from typing import Any

from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import Address


class IBlockchainService(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: Any) -> Any:
        return (
            hasattr(subclass, "create_address")
            and callable(subclass.load_data_source)
            or NotImplemented
        )

    @abc.abstractmethod
    def name(self) -> ChainServiceName:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_address(self, mnemonic: str) -> Address:
        raise NotImplementedError

    @abc.abstractmethod
    async def send(
        self,
        from_address: Address,
        to: str,
        value: float,
        token_asset: TokenAsset,
        mnemonic: str,
    ) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_balance(self, address: Address, token_asset: TokenAsset) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_transactions(
        self,
        address: Address,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block: int,
    ) -> list[Any]:
        raise NotImplementedError

    async def swap_between_wraps(
        self,
        value: float,
        mnemonic: str,
        token_asset: TokenAsset,
    ) -> str:
        pass

    async def get_test_token(
        self,
        to_address: str,
        value: float,
    ) -> str | list[str]:
        pass
