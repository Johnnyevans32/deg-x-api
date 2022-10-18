import abc
from typing import Any

from apps.blockchain.interfaces.blockchain_interface import Blockchain, ChainServiceName
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
        from_address: str,
        to: str,
        value: float,
        token_asset: TokenAsset,
        mnemonic: str,
    ) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_balance(self, address: str, token_asset: TokenAsset) -> float:
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

    async def swap_between_wraps(
        self,
        value: float,
        mnemonic: str,
        token_asset: TokenAsset,
    ) -> str:
        pass

    async def approve_token_delegation(
        self,
        network: Network,
        blockchain: Blockchain,
        mnemonic: str,
        amount: int,
        asset_address: Any,
        spender_address: Any,
    ) -> Any:
        pass

    async def sign_txn(
        self,
        network: Network,
        blockchain: Blockchain,
        mnemonic: str,
        txn_build: Any,
    ) -> Any:
        pass

    async def get_test_token(
        self,
        to_address: str,
        value: float,
    ) -> str:
        pass
