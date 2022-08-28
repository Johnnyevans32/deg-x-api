from typing import Any, cast

import base58
import spl.token.instructions as spl_token
from solana.publickey import PublicKey

from apps.appclient.services.beta_service import BetaService
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.solana.solana_service import SolanaService
from apps.defi.interfaces.defi_provider_interface import DefiProvider
from apps.defi.lending.aave.aave_interface import IReserveTokens, IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode
from apps.defi.lending.services.lending_service_interface import ILendingService
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

    async def get_user_config(self, user_addr: str, defi_provider: DefiProvider):
        pass

    async def deposit(
        self,
        asset: str,
        value: float,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        referral_code=0,
        gas=80000,
        gas_price=50,
    ):
        chain_network = cast(Network, defi_provider.network)
        client = await self.solanaService.get_network_provider(chain_network)

        sender = self.solanaService.get_keypair_from_mnemonic(mnemonic)

        solend_program_id = PublicKey(defi_provider.contractAddress)
        amount = int(self.solanaService.format_num(value, "to"))

        token_account = spl_token.get_associated_token_address(
            sender.public_key, PublicKey(asset)
        )
        appr_res = await self.solanaService.approve_spl_token_delegate(
            client,
            sender,
            solend_program_id,
            token_account,
            amount,
        )
        print(appr_res)
        # create txn of approval request
        solend_info = await get_solend_info(defi_provider)
        token_info = get_token_info(asset, solend_info)
        payload = {
            "providerUrl": chain_network.providerUrl,
            "amount": amount,
            "symbol": token_info.symbol,
            "userAddress": str(sender.public_key),
            "secretKey": str(base58.b58encode(sender.secret_key), "utf-8"),
            "cluster": "devnet"
            if chain_network.networkType == NetworkType.TESTNET
            else "production",
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
        gas=70000,
        gas_price=50,
    ) -> Any:
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
            "cluster": "devnet"
            if chain_network.networkType == NetworkType.TESTNET
            else "production",
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
        referral_code=0,
        gas=70000,
        gas_price=50,
    ):
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
            "cluster": "devnet"
            if chain_network.networkType == NetworkType.TESTNET
            else "production",
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
        gas=40000,
        gas_price=50,
    ) -> Any:
        chain_network = cast(Network, defi_provider.network)
        client = await self.solanaService.get_network_provider(chain_network)

        sender = self.solanaService.get_keypair_from_mnemonic(mnemonic)

        solend_program_id = PublicKey(defi_provider.contractAddress)
        amount = int(self.solanaService.format_num(value, "to"))

        token_account = spl_token.get_associated_token_address(
            sender.public_key, PublicKey(asset)
        )
        appr_res = await self.solanaService.approve_spl_token_delegate(
            client,
            sender,
            solend_program_id,
            token_account,
            amount,
        )
        print(appr_res)
        # create txn of approval request
        solend_info = await get_solend_info(defi_provider)
        token_info = get_token_info(asset, solend_info)
        payload = {
            "providerUrl": chain_network.providerUrl,
            "amount": amount,
            "symbol": token_info.symbol,
            "userAddress": str(sender.public_key),
            "secretKey": str(base58.b58encode(sender.secret_key), "utf-8"),
            "cluster": "devnet"
            if chain_network.networkType == NetworkType.TESTNET
            else "production",
        }

        repayRes = await self.betaService.interact_on_solend("repay", payload)

        return repayRes

    async def swap_borrow_rate_mode(
        self,
        asset: str,
        rate_mode: int,
        defi_provider: DefiProvider,
    ):
        pass

    async def set_user_use_reserve_as_collateral(
        self,
        asset: str,
        use_as_collateral: bool,
        defi_provider: DefiProvider,
    ):
        pass

    @timed_cache(10, 10, asyncFunction=True)
    async def get_reserve_assets(
        self, defi_provider: DefiProvider
    ) -> list[IReserveTokens]:
        solend_info = await get_solend_info(defi_provider)
        reserve_tokens = list(
            map(
                lambda asset: IReserveTokens(
                    **{"tokenSymbol": asset.symbol, "tokenAddress": asset.mintAddress}
                ),
                solend_info.assets,
            )
        )
        return reserve_tokens
