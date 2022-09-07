from enum import IntEnum
from typing import Any, cast

import spl.token.instructions as spl_token
from construct import Bytes, Int8ul, Int32ul, Int64ul, Pass
from construct import Struct as cStruct
from construct import Switch
from pydantic import BaseModel
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.sysvar import SYSVAR_CLOCK_PUBKEY, SYSVAR_RENT_PUBKEY
from solana.transaction import AccountMeta, TransactionInstruction
from solana.utils.helpers import decode_byte_string
from spl.token.constants import TOKEN_PROGRAM_ID

from apps.blockchain.solana.solana_utils import get_token_account
from apps.defi.interfaces.defiprovider_interface import DefiProvider
from apps.defi.lending.solend.solend_types import (
    ISolendMarketReserve,
    OracleAsset,
    SolendAsset,
    SolendMarket,
    SolendReserve,
)
from core.utils.request import REQUEST_METHOD, HTTPRepository
from core.utils.utils_service import timed_cache

httpRepository = HTTPRepository()


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


def get_token_info(mint_address: str, solend_info: ISolendMarketReserve) -> SolendAsset:
    token_info = list(
        filter(lambda asset: asset.mintAddress == mint_address, solend_info.assets)
    )[0]
    if not token_info:
        raise Exception(f"Could not find {mint_address} in ASSETS")
    return token_info


@timed_cache(100, 10, asyncFunction=True)
async def get_solend_info(
    defi_provider: DefiProvider,
) -> ISolendMarketReserve:
    assert defi_provider.meta, "solend metadata not found"
    url = (
        f"{defi_provider.meta['API_ENDPOINT']}/"
        f"v1/config?deployment={defi_provider.meta['ENV']}"
    )

    solend_info = await httpRepository.call(
        REQUEST_METHOD.GET,
        url,
        ISolendMarketReserve,
    )

    return solend_info


class Key(BaseModel):
    pubkey: PublicKey
    is_signer: bool
    is_writable: bool

    class Config:
        arbitrary_types_allowed = True


# @lru_cache(128)
def get_deposit_reserve_keys(
    sourceLiquidity: PublicKey,
    sourceCollateral: PublicKey,
    reserve: PublicKey,
    reserveLiquiditySupply: PublicKey,
    reserveCollateralMint: PublicKey,
    lendingMarket: PublicKey,
    lendingMarketAuthority: PublicKey,
    destinationCollateral: PublicKey,
    obligation: PublicKey,
    obligationOwner: PublicKey,
    pythOracle: PublicKey,
    switchboardFeedAddress: PublicKey,
    transferAuthority: PublicKey,
) -> list[AccountMeta]:
    keys: list[dict[str, PublicKey | bool]] = [
        {"pubkey": sourceLiquidity, "is_signer": False, "is_writable": True},
        {
            "pubkey": sourceCollateral,
            "is_signer": False,
            "is_writable": True,
        },
        {"pubkey": reserve, "is_signer": False, "is_writable": True},
        {
            "pubkey": reserveLiquiditySupply,
            "is_signer": False,
            "is_writable": True,
        },
        {
            "pubkey": reserveCollateralMint,
            "is_signer": False,
            "is_writable": True,
        },
        {"pubkey": lendingMarket, "is_signer": False, "is_writable": True},
        {
            "pubkey": lendingMarketAuthority,
            "is_signer": False,
            "is_writable": False,
        },
        {
            "pubkey": destinationCollateral,
            "is_signer": False,
            "is_writable": True,
        },
        {"pubkey": obligation, "is_signer": False, "is_writable": True},
        {"pubkey": obligationOwner, "is_signer": True, "is_writable": False},
        {"pubkey": pythOracle, "is_signer": False, "is_writable": False},
        {
            "pubkey": switchboardFeedAddress,
            "is_signer": False,
            "is_writable": False,
        },
        {
            "pubkey": transferAuthority,
            "is_signer": True,
            "is_writable": False,
        },
        {
            "pubkey": SYSVAR_CLOCK_PUBKEY,
            "is_signer": False,
            "is_writable": False,
        },
        {
            "pubkey": TOKEN_PROGRAM_ID,
            "is_signer": False,
            "is_writable": False,
        },
    ]

    return list(
        map(
            lambda key: AccountMeta(
                pubkey=cast(PublicKey, key["pubkey"]),
                is_signer=cast(bool, key["is_signer"]),
                is_writable=cast(bool, key["is_writable"]),
            ),
            keys,
        )
    )


# @lru_cache(128)
def get_withdraw_reserve_keys(
    sourceCollateral: PublicKey,
    destinationCollateral: PublicKey,
    withdrawReserve: PublicKey,
    obligation: PublicKey,
    lendingMarket: PublicKey,
    lendingMarketAuthority: PublicKey,
    destinationLiquidity: PublicKey,
    reserveCollateralMint: PublicKey,
    reserveLiquiditySupply: PublicKey,
    obligationOwner: PublicKey,
    transferAuthority: PublicKey,
) -> list[AccountMeta]:
    keys: list[dict[str, PublicKey | bool]] = [
        {
            "pubkey": sourceCollateral,
            "is_signer": False,
            "is_writable": True,
        },
        {
            "pubkey": destinationCollateral,
            "is_signer": False,
            "is_writable": True,
        },
        {"pubkey": withdrawReserve, "is_signer": False, "is_writable": True},
        {"pubkey": obligation, "is_signer": False, "is_writable": True},
        {"pubkey": lendingMarket, "is_signer": False, "is_writable": False},
        {
            "pubkey": lendingMarketAuthority,
            "is_signer": False,
            "is_writable": False,
        },
        {
            "pubkey": destinationLiquidity,
            "is_signer": False,
            "is_writable": True,
        },
        {
            "pubkey": reserveCollateralMint,
            "is_signer": False,
            "is_writable": True,
        },
        {
            "pubkey": reserveLiquiditySupply,
            "is_signer": False,
            "is_writable": True,
        },
        {"pubkey": obligationOwner, "is_signer": True, "is_writable": False},
        {
            "pubkey": transferAuthority,
            "is_signer": True,
            "is_writable": False,
        },
        {
            "pubkey": SYSVAR_CLOCK_PUBKEY,
            "is_signer": False,
            "is_writable": False,
        },
        {
            "pubkey": TOKEN_PROGRAM_ID,
            "is_signer": False,
            "is_writable": False,
        },
    ]

    return list(
        map(
            lambda key: AccountMeta(
                pubkey=cast(PublicKey, key["pubkey"]),
                is_signer=cast(bool, key["is_signer"]),
                is_writable=cast(bool, key["is_writable"]),
            ),
            keys,
        )
    )


# @lru_cache(128)
def get_borrow_reserve_keys(
    sourceLiquidity: PublicKey,
    destinationLiquidity: PublicKey,
    borrowReserve: PublicKey,
    borrowReserveLiquidityFeeReceiver: PublicKey,
    obligation: PublicKey,
    lendingMarket: PublicKey,
    lendingMarketAuthority: PublicKey,
    obligationOwner: PublicKey,
) -> list[AccountMeta]:
    keys: list[dict[str, PublicKey | bool]] = [
        {"pubkey": sourceLiquidity, "is_signer": False, "is_writable": True},
        {
            "pubkey": destinationLiquidity,
            "is_signer": False,
            "is_writable": True,
        },
        {"pubkey": borrowReserve, "is_signer": False, "is_writable": True},
        {
            "pubkey": borrowReserveLiquidityFeeReceiver,
            "is_signer": False,
            "is_writable": True,
        },
        {"pubkey": obligation, "is_signer": False, "is_writable": True},
        {"pubkey": lendingMarket, "is_signer": False, "is_writable": False},
        {
            "pubkey": lendingMarketAuthority,
            "is_signer": False,
            "is_writable": False,
        },
        {"pubkey": obligationOwner, "is_signer": True, "is_writable": False},
        {
            "pubkey": SYSVAR_CLOCK_PUBKEY,
            "is_signer": False,
            "is_writable": False,
        },
        {
            "pubkey": TOKEN_PROGRAM_ID,
            "is_signer": False,
            "is_writable": False,
        },
    ]

    return list(
        map(
            lambda key: AccountMeta(
                pubkey=cast(PublicKey, key["pubkey"]),
                is_signer=cast(bool, key["is_signer"]),
                is_writable=cast(bool, key["is_writable"]),
            ),
            keys,
        )
    )


# @lru_cache(128)
def get_repay_reserve_keys(
    sourceLiquidity: PublicKey,
    destinationLiquidity: PublicKey,
    repayReserve: PublicKey,
    obligation: PublicKey,
    lendingMarket: PublicKey,
    transferAuthority: PublicKey,
) -> list[AccountMeta]:
    keys: list[dict[str, PublicKey | bool]] = [
        {"pubkey": sourceLiquidity, "is_signer": False, "is_writable": True},
        {
            "pubkey": destinationLiquidity,
            "is_signer": False,
            "is_writable": True,
        },
        {"pubkey": repayReserve, "is_signer": False, "is_writable": True},
        {"pubkey": obligation, "is_signer": False, "is_writable": True},
        {"pubkey": lendingMarket, "is_signer": False, "is_writable": False},
        {
            "pubkey": transferAuthority,
            "is_signer": True,
            "is_writable": False,
        },
        {
            "pubkey": SYSVAR_CLOCK_PUBKEY,
            "is_signer": False,
            "is_writable": False,
        },
        {
            "pubkey": TOKEN_PROGRAM_ID,
            "is_signer": False,
            "is_writable": False,
        },
    ]

    return list(
        map(
            lambda key: AccountMeta(
                pubkey=cast(PublicKey, key["pubkey"]),
                is_signer=cast(bool, key["is_signer"]),
                is_writable=cast(bool, key["is_writable"]),
            ),
            keys,
        )
    )


def get_init_obligation_keys(
    obligation: PublicKey,
    lendingMarket: PublicKey,
    obligationOwner: PublicKey,
    solendProgramAddress: PublicKey,
) -> list[AccountMeta]:

    keys: list[dict[str, PublicKey | bool]] = [
        {"pubkey": obligation, "is_signer": False, "is_writable": True},
        {
            "pubkey": lendingMarket,
            "is_signer": False,
            "is_writable": False,
        },
        {"pubkey": obligationOwner, "is_signer": True, "is_writable": False},
        {
            "pubkey": SYSVAR_CLOCK_PUBKEY,
            "is_signer": False,
            "is_writable": False,
        },
        {
            "pubkey": SYSVAR_RENT_PUBKEY,
            "is_signer": False,
            "is_writable": False,
        },
        {
            "pubkey": TOKEN_PROGRAM_ID,
            "is_signer": False,
            "is_writable": False,
        },
    ]

    return list(
        map(
            lambda key: AccountMeta(
                pubkey=cast(PublicKey, key["pubkey"]),
                is_signer=cast(bool, key["is_signer"]),
                is_writable=cast(bool, key["is_writable"]),
            ),
            keys,
        )
    )


async def get_instruction_data(
    defi_provider: DefiProvider,
    mint_address: str,
    user_addr: PublicKey,
    martket_addr: str = None,
) -> tuple[SolendMarket, PublicKey, SolendReserve, OracleAsset]:
    solend_info = await get_solend_info(defi_provider)
    token_info = get_token_info(mint_address, solend_info)

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
        filter(lambda ora: ora.asset == token_info.symbol, solend_info.oracles.assets)
    )[0]

    return lending_market, obligation_address, reserve, oracle_info


async def get_withdraw_instruction_keys(
    defi_provider: DefiProvider,
    mint_address: str,
    user_token_address: PublicKey,
    user_addr: PublicKey,
    martket_addr: str = None,
) -> list[AccountMeta]:
    (
        lending_market,
        obligation_address,
        reserve,
        _,
    ) = await get_instruction_data(defi_provider, mint_address, user_addr, martket_addr)

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
    defi_provider: DefiProvider,
    mint_address: str,
    user_token_address: PublicKey,
    user_addr: PublicKey,
    martket_addr: str = None,
) -> list[AccountMeta]:
    (
        lending_market,
        obligation_address,
        reserve,
        _,
    ) = await get_instruction_data(defi_provider, mint_address, user_addr, martket_addr)

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
    client: AsyncClient,
    defi_provider: DefiProvider,
    mint_address: str,
    user_token_address: PublicKey,
    user_addr: PublicKey,
    solend_program_id: PublicKey,
    martket_addr: str = None,
) -> list[AccountMeta]:
    (
        lending_market,
        obligation_address,
        reserve,
        oracle_info,
    ) = await get_instruction_data(defi_provider, mint_address, user_addr, martket_addr)

    user_collateral_address = spl_token.get_associated_token_address(
        user_addr,
        PublicKey(reserve.collateralMintAddress),
    )

    return get_deposit_reserve_keys(
        user_token_address,
        user_collateral_address,
        PublicKey(reserve.address),
        PublicKey(reserve.liquidityAddress),
        PublicKey(reserve.collateralMintAddress),
        PublicKey(lending_market.address),
        PublicKey(lending_market.authorityAddress),
        PublicKey(reserve.collateralSupplyAddress),
        obligation_address,
        user_addr,
        PublicKey(oracle_info.priceAddress),
        PublicKey(oracle_info.switchboardFeedAddress),
        user_addr,
    )


DEPOSIT_PARAMS = cStruct("liquidity_amount" / Int64ul)

SOLEND_INSTRUCTION_LAYOUT = cStruct(
    "instruction_type" / Int32ul,
    "args"
    / Switch(
        lambda this: this.instruction_type,
        {
            SolendInstructionType.DepositReserveAndObligation: DEPOSIT_PARAMS,
            SolendInstructionType.InitObligation: Pass,
        },
    ),
)


async def init_obligation_instruction(
    client: AsyncClient,
    obligation_addr: PublicKey,
    lending_market_addr: PublicKey,
    user_addr: PublicKey,
    solend_program_id: PublicKey,
) -> TransactionInstruction:

    obligation_acc = await get_token_account(client, obligation_addr)
    print("obligation_acc", obligation_acc)
    try:
        obligation_details = parse_obligation(obligation_acc)
    except Exception as e:
        print("obligation error", e)
    obligation_details
    data_layout = SOLEND_INSTRUCTION_LAYOUT.build(
        dict(instruction_type=SolendInstructionType.InitObligation, args=None)
    )
    txn_key = get_init_obligation_keys(
        obligation_addr, lending_market_addr, user_addr, solend_program_id
    )

    return TransactionInstruction(
        keys=txn_key,
        program_id=solend_program_id,
        data=data_layout,
    )


class ObligationCollateral(BaseModel):
    depositReserve: PublicKey
    depositedAmount: float
    marketValue: float

    class Config:
        arbitrary_types_allowed = True


class ObligationLiquidity(BaseModel):
    borrowReserve: PublicKey
    cumulativeBorrowRateWads: float
    borrowedAmountWads: float
    marketValue: float

    class Config:
        arbitrary_types_allowed = True


class LastUpdate(BaseModel):
    slot: float
    stale: bool

    class Config:
        arbitrary_types_allowed = True


class Obligation(BaseModel):
    version: float
    lastUpdate: LastUpdate
    lendingMarket: PublicKey
    owner: PublicKey
    deposits: list[ObligationCollateral]
    borrows: list[ObligationLiquidity]
    depositedValue: float
    borrowedValue: float
    allowedBorrowValue: float
    unhealthyBorrowValue: float

    class Config:
        arbitrary_types_allowed = True


PUBLIC_KEY_LAYOUT = Bytes(32)

LAST_UPDATE_LAYOUT = cStruct("slot" / Int64ul, "stale" / Int8ul)

OBLIGATION_LAYOUT = cStruct(
    "version" / Int8ul,
    "lastUpdate" / LAST_UPDATE_LAYOUT,
    "lendingMarket" / PUBLIC_KEY_LAYOUT,
    "owner" / PUBLIC_KEY_LAYOUT,
    "depositedValue" / Int64ul,
    "borrowedValue" / Int64ul,
    "allowedBorrowValue" / Int64ul,
    "unhealthyBorrowValue" / Int64ul,
    "depositsLen" / Int8ul,
    "borrowsLen" / Int8ul,
)

OBLIGATION_COLLATERAL_LAYOUT = cStruct(
    "depositReserve" / PUBLIC_KEY_LAYOUT,
    "depositedAmount" / Int64ul,
    "marketValue" / Int64ul,
)
OBLIGATION_LIQUIDITY_LAYOUT = cStruct(
    "borrowReserve" / PUBLIC_KEY_LAYOUT,
    "cumulativeBorrowRateWads" / Int64ul,
    "borrowedAmountWads" / Int64ul,
    "marketValue" / Int64ul,
)
OBLIGATION_SIZE = OBLIGATION_LAYOUT.sizeof()


class ProtoObligation(BaseModel):
    version: int
    lastUpdate: LastUpdate
    lendingMarket: PublicKey
    owner: PublicKey
    depositedValue: float
    borrowedValue: float
    allowedBorrowValue: float
    unhealthyBorrowValue: float
    depositsLen: int
    borrowsLen: int
    #   dataFlat: Buffer;

    class Config:
        arbitrary_types_allowed = True


def parse_obligation(info: Any) -> Any:
    bytes_data = decode_byte_string(info["result"]["value"]["data"][0])
    if len(bytes_data) != OBLIGATION_LAYOUT.sizeof():
        raise ValueError("Invalid account size")

    decoded_data = OBLIGATION_LAYOUT.parse(bytes_data)
    print(decoded_data)
    details = {
        "account": info,
        "info": decoded_data,
    }

    return details
