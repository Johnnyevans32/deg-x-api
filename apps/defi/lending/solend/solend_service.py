from typing import Any, cast

import base58
from solana.publickey import PublicKey

from apps.appclient.services.beta_service import BetaService
from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.solana.solana_service import SolanaService
from apps.defi.interfaces.defiprovider_interface import DefiProvider
from apps.defi.lending.types.lending_types import IReserveToken, IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode
from apps.defi.lending.services.lending_iservice import ILendingService
from apps.defi.lending.solend.solend_utils import get_solend_info, get_token_info
from core.utils.request import HTTPRepository
from core.utils.utils_service import timed_cache


class SolendService(ILendingService):
    solanaService = SolanaService()
    httpRepository = HTTPRepository()
    betaService = BetaService()

    def name(self) -> str:
        return "solend_service"

    async def get_user_account_data(
        self, user_addr: str, defi_provider: DefiProvider
    ) -> IUserAcccountData:
        pass

    async def get_user_config(self, user_addr: str, defi_provider: DefiProvider) -> Any:
        pass

    @staticmethod
    def get_cluster(networkType: NetworkType) -> str:
        return "devnet" if networkType == NetworkType.TESTNET else "production"

    async def deposit(
        self,
        asset: str,
        value: float,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        referral_code: int = 0,
        gas: int = 80000,
        gas_price: int = 50,
    ) -> str:
        chain_network = cast(Network, defi_provider.network)
        blockchain = cast(Blockchain, defi_provider.blockchain)
        amount = int(self.solanaService.format_num(value, "to"))

        await self.solanaService.approve_token_delegation(
            chain_network,
            blockchain,
            mnemonic,
            amount,
            PublicKey(asset),
            PublicKey(defi_provider.contractAddress),
        )
        # create txn of approval request
        solend_info = await get_solend_info(defi_provider)
        token_info = get_token_info(asset, solend_info)
        sender = self.solanaService.get_keypair_from_mnemonic(mnemonic)
        payload = {
            "providerUrl": chain_network.providerUrl,
            "amount": amount,
            "symbol": token_info.symbol,
            "userAddress": on_behalf_of,
            "secretKey": str(base58.b58encode(sender.secret_key), "utf-8"),
            "cluster": self.get_cluster(chain_network.networkType),
        }

        depositRes = await self.betaService.interact_on_solend("deposit", payload)

        return depositRes

    async def withdraw(
        self,
        asset: str,
        value: float,
        to: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        gas: int = 70000,
        gas_price: int = 50,
    ) -> str:
        chain_network = cast(Network, defi_provider.network)

        sender = self.solanaService.get_keypair_from_mnemonic(mnemonic)

        amount = int(self.solanaService.format_num(value, "to"))

        solend_info = await get_solend_info(defi_provider)
        token_info = get_token_info(asset, solend_info)
        payload = {
            "providerUrl": chain_network.providerUrl,
            "amount": amount,
            "symbol": token_info.symbol,
            "userAddress": str(sender.public_key),
            "secretKey": str(base58.b58encode(sender.secret_key), "utf-8"),
            "cluster": self.get_cluster(chain_network.networkType),
        }

        withdrawRes = await self.betaService.interact_on_solend("withdraw", payload)

        return withdrawRes

    async def borrow(
        self,
        asset: str,
        value: float,
        interest_rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        referral_code: int = 0,
        gas: int = 70000,
        gas_price: int = 50,
    ) -> str:
        chain_network = cast(Network, defi_provider.network)

        sender = self.solanaService.get_keypair_from_mnemonic(mnemonic)

        amount = int(self.solanaService.format_num(value, "to"))

        solend_info = await get_solend_info(defi_provider)
        token_info = get_token_info(asset, solend_info)
        payload = {
            "providerUrl": chain_network.providerUrl,
            "amount": amount,
            "symbol": token_info.symbol,
            "userAddress": str(sender.public_key),
            "secretKey": str(base58.b58encode(sender.secret_key), "utf-8"),
            "cluster": self.get_cluster(chain_network.networkType),
        }

        borrowRes = await self.betaService.interact_on_solend("borrow", payload)

        return borrowRes

    async def repay(
        self,
        asset: str,
        value: float,
        rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        gas: int = 40000,
        gas_price: int = 50,
    ) -> Any:
        chain_network = cast(Network, defi_provider.network)
        blockchain = cast(Blockchain, defi_provider.blockchain)
        sender = self.solanaService.get_keypair_from_mnemonic(mnemonic)

        amount = int(self.solanaService.format_num(value, "to"))

        await self.solanaService.approve_token_delegation(
            chain_network,
            blockchain,
            mnemonic,
            amount,
            PublicKey(asset),
            PublicKey(defi_provider.contractAddress),
        )
        # create txn of approval request
        solend_info = await get_solend_info(defi_provider)
        token_info = get_token_info(asset, solend_info)
        payload = {
            "providerUrl": chain_network.providerUrl,
            "amount": amount,
            "symbol": token_info.symbol,
            "userAddress": str(sender.public_key),
            "secretKey": str(base58.b58encode(sender.secret_key), "utf-8"),
            "cluster": self.get_cluster(chain_network.networkType),
        }

        repayRes = await self.betaService.interact_on_solend("repay", payload)

        return repayRes

    async def swap_borrow_rate_mode(
        self,
        asset: str,
        rate_mode: int,
        defi_provider: DefiProvider,
    ) -> Any:
        pass

    async def set_user_use_reserve_as_collateral(
        self,
        asset: str,
        use_as_collateral: bool,
        defi_provider: DefiProvider,
    ) -> Any:
        pass

    @timed_cache(10, 10, asyncFunction=True)
    async def get_reserve_assets(
        self, defi_provider: DefiProvider
    ) -> list[IReserveToken]:
        solend_info = await get_solend_info(defi_provider)
        reserve_tokens = list(
            map(
                lambda asset: IReserveToken(
                    **{"tokenSymbol": asset.symbol, "tokenAddress": asset.mintAddress}
                ),
                solend_info.assets,
            )
        )
        return reserve_tokens
