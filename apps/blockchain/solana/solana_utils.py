import asyncio
from enum import IntEnum
from typing import Union

import spl.token.instructions as spl_token
from construct import Int8ub, Pass
from construct import Struct as cStruct
from construct import Switch
from pydantic import BaseModel
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import RPCResponse
from solana.transaction import AccountMeta, Transaction, TransactionInstruction
from solana.utils.helpers import decode_byte_string
from spl.token._layouts import ACCOUNT_LAYOUT
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID, WRAPPED_SOL_MINT
from spl.token.core import AccountInfo


class InstructionType(IntEnum):
    """Token instruction types."""

    INITIALIZE_MINT = 0
    INITIALIZE_ACCOUNT = 1
    INITIALIZE_MULTISIG = 2
    TRANSFER = 3
    APPROVE = 4
    REVOKE = 5
    SET_AUTHORITY = 6
    MINT_TO = 7
    BURN = 8
    CLOSE_ACCOUNT = 9
    FREEZE_ACCOUNT = 10
    THAW_ACCOUNT = 11
    TRANSFER2 = 12
    APPROVE2 = 13
    MINT_TO2 = 14
    BURN2 = 15
    SYNCNATIVE = 17


INSTRUCTIONS_LAYOUT = cStruct(
    "instruction_type" / Int8ub,
    "args"
    / Switch(
        lambda this: this.instruction_type,
        {InstructionType.SYNCNATIVE: Pass},
    ),
)


class IRPCContext(BaseModel):
    apiVersion: str
    slot: int


class IRPCValue(BaseModel):
    amount: str
    decimals: int
    uiAmount: float
    uiAmountString: str


class IRPCResult(BaseModel):
    context: IRPCContext
    value: Union[IRPCValue, int]


class IRPCResponse(BaseModel):
    jsonrpc: str
    result: IRPCResult
    id: int


async def get_or_create_assoc_token_acc(
    solana_client: AsyncClient,
    sender: Keypair,
    owner: PublicKey,
    associated_token_account: PublicKey,
) -> AccountInfo:
    try:
        account = await get_token_account(solana_client, associated_token_account)
        print("account", account)
    except (ValueError, AttributeError) as e:
        err = str(e).strip().lower()
        print("err", err)
        if err == "invalid account owner" or err == "invalid account owner":
            balance_needed = (
                await AsyncToken.get_min_balance_rent_for_exempt_for_account(
                    solana_client
                )
            )
            print("balance_needed", balance_needed)
            ata_txn = Transaction().add(
                # sp.create_account(
                #     sp.CreateAccountParams(
                #         from_pubkey=sender.public_key,
                #         new_account_pubkey=associated_token_account,
                #         lamports=balance_needed,
                #         space=ACCOUNT_LAYOUT.sizeof(),
                #         program_id=TOKEN_PROGRAM_ID,
                #     )
                # )
                spl_token.create_associated_token_account(
                    sender.public_key, owner, WRAPPED_SOL_MINT
                )
            )
            await solana_client.send_transaction(
                ata_txn,
                sender,
            )
            # after creation of token account it takes some moments for txn to get mined
            # and this get account to work so we might need to do a callback time sleep
            await asyncio.sleep(1)
            account = await get_token_account(solana_client, associated_token_account)
        else:
            raise e

    return account


async def get_token_account(client: AsyncClient, addr: PublicKey) -> AccountInfo:
    """Retrieve token account information.

    Args:
        client: The solana async client connection.
        addr: The pubkey of the token account.

    Returns:
        The parsed `AccountInfo` of the token account.
    """
    depositor_acc_info_raw = await client.get_account_info(addr)
    print("depositor_acc_info_raw", depositor_acc_info_raw)
    return parse_token_account(depositor_acc_info_raw)


async def sync_native(
    solana_client: AsyncClient, sender: Keypair, token_account: PublicKey
) -> None:
    sync_native_txn = Transaction().add(create_sync_native_instruction(token_account))
    await solana_client.send_transaction(
        sync_native_txn,
        sender,
    )


def create_sync_native_instruction(token_account: PublicKey) -> TransactionInstruction:
    data = INSTRUCTIONS_LAYOUT.build(
        dict(instruction_type=InstructionType.SYNCNATIVE, args=None)
    )
    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=token_account, is_signer=False, is_writable=True),
        ],
        program_id=TOKEN_PROGRAM_ID,
        data=data,
    )


def parse_token_account(info: RPCResponse) -> AccountInfo:
    """Parse `AccountInfo` from RPC response.

    Args:
        info: the `get_account_info` RPC response.

    Raises:
        ValueError: If the fetched data is the wrong size.
        AttributeError: If the account is not owned by the token program.

    Returns:
        The parsed `AccountInfo`.
    """
    if not info or not info["result"]["value"]:
        raise ValueError("Invalid account owner")

    if info["result"]["value"]["owner"] != str(TOKEN_PROGRAM_ID):
        raise AttributeError("Invalid account owner")

    bytes_data = decode_byte_string(info["result"]["value"]["data"][0])
    if len(bytes_data) != ACCOUNT_LAYOUT.sizeof():
        raise ValueError("Invalid account size")

    decoded_data = ACCOUNT_LAYOUT.parse(bytes_data)

    mint = PublicKey(decoded_data.mint)
    owner = PublicKey(decoded_data.owner)
    amount = decoded_data.amount

    if decoded_data.delegate_option == 0:
        delegate = None
        delegated_amount = 0
    else:
        delegate = PublicKey(decoded_data.delegate)
        delegated_amount = decoded_data.delegated_amount

    is_initialized = decoded_data.state != 0
    is_frozen = decoded_data.state == 2

    if decoded_data.is_native_option == 1:
        rent_exempt_reserve = decoded_data.is_native
        is_native = True
    else:
        rent_exempt_reserve = None
        is_native = False

    if decoded_data.close_authority_option == 0:
        close_authority = None
    else:
        close_authority = PublicKey(decoded_data.owner)

    return AccountInfo(
        mint,
        owner,
        amount,
        delegate,
        delegated_amount,
        is_initialized,
        is_frozen,
        is_native,
        rent_exempt_reserve,
        close_authority,
    )
