from functools import lru_cache
from typing import List, cast

from pydantic import BaseModel
from solana.publickey import PublicKey
from solana.sysvar import SYSVAR_CLOCK_PUBKEY
from solana.transaction import AccountMeta
from spl.token.constants import TOKEN_PROGRAM_ID


class Key(BaseModel):
    pubkey: PublicKey
    is_signer: bool
    is_writable: bool

    class Config:
        arbitrary_types_allowed = True


@lru_cache(128)
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
):
    keys = [
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

    c_keys = cast(List[Key], keys)
    return list(
        map(
            lambda key: AccountMeta(
                pubkey=key.pubkey,
                is_signer=key.is_signer,
                is_writable=key.is_writable,
            ),
            c_keys,
        )
    )


@lru_cache(128)
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
):
    keys = [
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

    c_keys = cast(List[Key], keys)
    return list(
        map(
            lambda key: AccountMeta(
                pubkey=key.pubkey,
                is_signer=key.is_signer,
                is_writable=key.is_writable,
            ),
            c_keys,
        )
    )


def get_borrow_reserve_keys(
    sourceLiquidity: PublicKey,
    destinationLiquidity: PublicKey,
    borrowReserve: PublicKey,
    borrowReserveLiquidityFeeReceiver: PublicKey,
    obligation: PublicKey,
    lendingMarket: PublicKey,
    lendingMarketAuthority: PublicKey,
    obligationOwner: PublicKey,
):
    keys = [
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

    c_keys = cast(List[Key], keys)
    return list(
        map(
            lambda key: AccountMeta(
                pubkey=key.pubkey,
                is_signer=key.is_signer,
                is_writable=key.is_writable,
            ),
            c_keys,
        )
    )


@lru_cache(128)
def get_repay_reserve_keys(
    sourceLiquidity: PublicKey,
    destinationLiquidity: PublicKey,
    repayReserve: PublicKey,
    obligation: PublicKey,
    lendingMarket: PublicKey,
    transferAuthority: PublicKey,
):
    keys = [
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

    c_keys = cast(List[Key], keys)
    return list(
        map(
            lambda key: AccountMeta(
                pubkey=key.pubkey,
                is_signer=key.is_signer,
                is_writable=key.is_writable,
            ),
            c_keys,
        )
    )
