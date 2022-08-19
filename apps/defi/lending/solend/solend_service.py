from enum import IntEnum
from typing import Any, cast

import spl.token.instructions as spl_token
from construct import Switch  # type: ignore
from construct import Int32ul, Int64ul
from construct import Struct as cStruct
from solana.publickey import PublicKey
from solana.system_program import TransactionInstruction
from solana.transaction import Transaction

from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.solana.solana_service import SolanaService
from apps.defi.interfaces.defi_provider_interface import DefiProvider
from apps.defi.lending.aave.aave_interface import IReserveTokens, IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode
from apps.defi.lending.services.lending_service_interface import ILendingService
from apps.defi.lending.solend.solend_types import (
    ISolendMarketReserve,
    OracleAsset,
    SolendMarket,
    SolendReserve,
)
from apps.defi.lending.solend.solend_utils import (
    get_borrow_reserve_keys,
    get_deposit_reserve_keys,
    get_withdraw_reserve_keys,
)
from core.utils.request import HTTPRepository
from core.utils.utils_service import timed_cache


class SolendInstructionType(IntEnum):
    InitLendingMarket = 0
    SetLendingMarketOwner = 1
    InitReserve = 2
    RefreshReserve = 3
    DepositReserveLiquidity = 4
    RedeemReserveCollateral = 5
    InitObligation = 6
    RefreshObligation = 7
    DepositObligationCollateral = 8
    WithdrawObligationCollateral = 9
    BorrowObligationLiquidity = 10
    RepayObligationLiquidity = 11
    LiquidateObligation = 12
    FlashLoan = 13
    DepositReserveAndObligation = 14
    WithdrawObligationAndReserveLiquidity = 15
    UpdateReserveConfig = 16


class SolendService(ILendingService):
    solanaService = SolanaService()
    httpRepository = HTTPRepository()

    def name(self) -> str:
        return "solend_service"

    @staticmethod
    def get_instruction_layout():
        DEPOSIT_PARAMS = cStruct("liquidity_amount" / Int64ul)
        # REPAY_PARAMS = cStruct("" / Int64ul)
        # WITHDRAW_PARAMS = cStruct("" / Int64ul)
        # BORROW_PARAMS = cStruct("" / Int64ul)
        return cStruct(
            "instruction_type" / Int32ul,
            "args"
            / Switch(
                lambda this: this.instruction_type,
                {
                    SolendInstructionType.DepositReserveAndObligation: DEPOSIT_PARAMS,
                },
            ),
        )

    def get_token_info(self, mint_address: str, solend_info: ISolendMarketReserve):
        token_info = list(
            filter(lambda asset: asset.mintAddress == mint_address, solend_info.assets)
        )[0]
        if not token_info:
            raise Exception(f"Could not find {mint_address} in ASSETS")
        return token_info

    @timed_cache(100, 10, asyncFunction=True)
    async def get_solend_info(
        self,
        defi_provider: DefiProvider,
    ):
        assert defi_provider.meta, "solend metadata not found"
        url = (
            f"{defi_provider.meta['API_ENDPOINT']}/"
            f"v1/config?deployment={defi_provider.meta['ENV']}"
        )

        solend_info = await self.httpRepository.call(
            "GET",
            url,
            ISolendMarketReserve,
        )

        return solend_info

    async def get_instruction_data(
        self,
        defi_provider: DefiProvider,
        mint_address: str,
        user_addr: PublicKey,
        martket_addr: str = None,
    ) -> tuple[SolendMarket, PublicKey, SolendReserve, OracleAsset]:
        solend_info = await self.get_solend_info(defi_provider)
        token_info = self.get_token_info(mint_address, solend_info)

        lending_market = list(
            filter(
                lambda market: market.address == martket_addr or market.isPrimary,
                solend_info.markets,
            )
        )[0]

        seed = str(lending_market.address)[:32]

        obligation_address = PublicKey.create_with_seed(
            user_addr, seed, PublicKey(solend_info.programID)
        )
        reserve = list(
            filter(
                lambda res: res.asset == token_info.symbol,
                lending_market.reserves,
            )
        )[0]
        if not reserve:
            raise Exception(f"Could not find asset {token_info.symbol} in reserves")

        oracle_info = list(
            filter(
                lambda ora: ora.asset == token_info.symbol, solend_info.oracles.assets
            )
        )[0]

        return lending_market, obligation_address, reserve, oracle_info

    async def get_withdraw_instruction_keys(
        self,
        defi_provider: DefiProvider,
        mint_address: str,
        user_token_address: PublicKey,
        user_addr: PublicKey,
        martket_addr: str = None,
    ):
        (
            lending_market,
            obligation_address,
            reserve,
            _,
        ) = await self.get_instruction_data(
            defi_provider, mint_address, user_addr, martket_addr
        )

        user_collateral_address = spl_token.get_associated_token_address(
            user_addr,
            PublicKey(reserve.collateralMintAddress),
        )

        return get_withdraw_reserve_keys(
            PublicKey(reserve.collateralSupplyAddress),
            user_collateral_address,
            PublicKey(reserve.address),
            obligation_address,
            PublicKey(lending_market.address),
            PublicKey(lending_market.authorityAddress),
            user_token_address,
            PublicKey(reserve.collateralMintAddress),
            PublicKey(reserve.liquidityAddress),
            user_addr,
            user_addr,
        )

    async def get_borrow_instruction_keys(
        self,
        defi_provider: DefiProvider,
        mint_address: str,
        user_token_address: PublicKey,
        user_addr: PublicKey,
        martket_addr: str = None,
    ):
        (
            lending_market,
            obligation_address,
            reserve,
            _,
        ) = await self.get_instruction_data(
            defi_provider, mint_address, user_addr, martket_addr
        )

        return get_borrow_reserve_keys(
            PublicKey(reserve.liquidityAddress),
            user_token_address,
            PublicKey(reserve.address),
            PublicKey(reserve.liquidityFeeReceiverAddress),
            obligation_address,
            PublicKey(lending_market.address),
            PublicKey(lending_market.authorityAddress),
            user_addr,
        )

    async def get_deposit_instruction_keys(
        self,
        defi_provider: DefiProvider,
        mint_address: str,
        user_token_address: PublicKey,
        user_addr: PublicKey,
        martket_addr: str = None,
    ):
        (
            lending_market,
            obligation_address,
            reserve,
            oracle_info,
        ) = await self.get_instruction_data(
            defi_provider, mint_address, user_addr, martket_addr
        )

        user_collateral_address = spl_token.get_associated_token_address(
            user_addr,
            PublicKey(reserve.collateralMintAddress),
        )

        return get_deposit_reserve_keys(
            str(user_token_address),
            str(user_collateral_address),
            reserve.address,
            reserve.liquidityAddress,
            reserve.collateralMintAddress,
            lending_market.address,
            lending_market.authorityAddress,
            PublicKey(reserve.collateralSupplyAddress),
            str(obligation_address),
            str(user_addr),
            PublicKey(oracle_info.priceAddress),
            PublicKey(oracle_info.switchboardFeedAddress),
            str(user_addr),
        )

    async def get_user_account_data(
        self, user_addr: str, defi_provider: DefiProvider
    ) -> IUserAcccountData:
        pass

    async def get_user_config(self, user_addr: str, defi_provider: DefiProvider):
        pass

    async def deposit(
        self,
        asset: str,
        amount: float,
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
        amount = int(self.solanaService.format_num(amount, "to"))

        token_account = spl_token.get_associated_token_address(
            sender.public_key, PublicKey(asset)
        )
        # appr_res = await self.solanaService.approve_spl_token_delegate(
        #     client,
        #     sender,
        #     solend_program_id,
        #     token_account,
        #     amount,
        # )
        # print("appr_res", appr_res, token_account)
        data = SolendService.get_instruction_layout().build(
            dict(
                instruction_type=SolendInstructionType.DepositReserveAndObligation,
                args=dict(liquidity_amount=amount),
            )
        )
        txn_key = await self.get_deposit_instruction_keys(
            defi_provider, asset, token_account, sender.public_key
        )

        transaction = Transaction().add(
            TransactionInstruction(
                keys=txn_key,
                program_id=solend_program_id,
                data=data,
            )
        )
        resp = await client.send_transaction(transaction, sender)
        print(resp)

        return resp

    async def withdraw(
        self,
        asset: str,
        amount: int,
        to: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        gas=70000,
        gas_price=50,
    ) -> Any:
        pass

    async def borrow(
        self,
        asset: str,
        amount: float,
        interest_rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        referral_code=0,
        gas=70000,
        gas_price=50,
    ):
        pass

    async def repay(
        self,
        asset: str,
        amount: float,
        rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        gas=40000,
        gas_price=50,
    ) -> Any:

        pass

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
        solend_info = await self.get_solend_info(defi_provider)
        reserve_tokens = list(
            map(
                lambda asset: IReserveTokens(
                    **{"tokenSymbol": asset.symbol, "tokenAddress": asset.mintAddress}
                ),
                solend_info.assets,
            )
        )
        return reserve_tokens
