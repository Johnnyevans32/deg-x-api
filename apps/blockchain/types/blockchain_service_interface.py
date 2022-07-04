import abc
from typing import Any


from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet


class IBlockchainService(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "create_address")
            and callable(subclass.load_data_source)
            or NotImplemented
        )

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def create_address(self, mnemonic: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def send(
        self,
        from_address: str,
        to: str,
        value: float,
        token_asset: TokenAsset,
        private_key: str,
    ) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_balance(self, address: str, token_asset: TokenAsset) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_transactions(
        self,
        address: str,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block: int,
    ) -> list[Any]:
        raise NotImplementedError
