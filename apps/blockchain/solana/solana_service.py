from typing import Any, Callable, cast

import spl.token.instructions as spl_token
from mnemonic import Mnemonic
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import RPCResponse, TokenAccountOpts
from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID, WRAPPED_SOL_MINT

from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.solana.solana_utils import (
    create_sync_native_instruction,
    get_or_create_assoc_token_acc,
)
from apps.blockchain.types.blockchain_service_interface import IBlockchainService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import Address
from core.utils.model_utility_service import ModelUtilityService
from core.utils.request import HTTPRepository


class SolanaService(IBlockchainService):
    httpRepository = HTTPRepository()
    mnemo = Mnemonic("english")

    def __init__(self) -> None:
        self.format_num: Callable[[int | float, str], int | float] = (
            lambda num, num_type: num * 10**9 if num_type == "to" else num / 10**9
        )

    def name(self) -> ChainServiceName:
        return ChainServiceName.SOL

    async def get_network_provider(self, network: Network) -> AsyncClient:
        solana_client = AsyncClient(network.providerUrl)
        # res = await solana_client.is_connected()
        return solana_client

    async def create_address(self, mnemonic: str) -> Address:
        keypair = self.get_keypair_from_mnemonic(mnemonic)

        return Address(**{"main": str(keypair.public_key)})

    def get_keypair_from_mnemonic(self, mnemonic: str) -> Keypair:
        seed = self.mnemo.to_seed(mnemonic)
        keypair = Keypair.from_secret_key(seed)
        return keypair

    async def get_txn_fee(self, client: AsyncClient, ACCOUNT_SIZE: int) -> int:
        fees = 0
        # if (!payer):
        fee_calculator = (await client.get_recent_blockhash())["result"]["value"][
            "feeCalculator"
        ]
        # // Calculate the cost to fund the greeter account
        fees += cast(
            int, await client.get_minimum_balance_for_rent_exemption(ACCOUNT_SIZE)
        )
        # // Calculate the cost of sending transactions
        fees += fee_calculator["lamportsPerSignature"] * 100
        # payer = await getPayer()

        return fees

    async def check_if_payee_balance_cover_fees(
        self, client: AsyncClient, address: PublicKey
    ) -> None:
        lamports = int((await client.get_balance(address))["result"]["value"])
        fees = await self.get_txn_fee(client, 20)
        if lamports < fees:
            # // If current balance is not enough to pay for fees, request an airdrop
            raise Exception("user solana acount balance doesnt cover fees")

    async def send(
        self,
        address_obj: Address,
        to_address: str,
        value: float,
        token_asset: TokenAsset,
        mnemonic: str,
        gas: int = 2000000,
        gas_price: int = 50,
    ) -> str:
        try:
            sender = self.get_keypair_from_mnemonic(mnemonic)
            chain_network = cast(Network, token_asset.network)
            solana_client = await self.get_network_provider(chain_network)

            amount = int(self.format_num(value, "to"))
            if token_asset.contractAddress:
                from_token_account = spl_token.get_associated_token_address(
                    sender.public_key,
                    PublicKey(token_asset.contractAddress),
                )
                to_token_account = spl_token.get_associated_token_address(
                    PublicKey(to_address),
                    PublicKey(token_asset.contractAddress),
                )
                acc1 = await get_or_create_assoc_token_acc(
                    solana_client, sender, sender.public_key, from_token_account
                )
                print(acc1)
                acc2 = await get_or_create_assoc_token_acc(
                    solana_client, sender, PublicKey(to_address), to_token_account
                )
                print(acc2)
                txn = spl_token.transfer(
                    spl_token.TransferParams(
                        program_id=TOKEN_PROGRAM_ID,
                        source=from_token_account,
                        dest=to_token_account,
                        owner=sender.public_key,
                        amount=amount,
                    )
                )
            else:
                txn = transfer(
                    TransferParams(
                        from_pubkey=sender.public_key,
                        to_pubkey=PublicKey(to_address),
                        lamports=amount,
                    )
                )
            txn_build = Transaction().add(txn)
            resp = await solana_client.send_transaction(txn_build, sender)

            return str(resp["result"])

        except Exception as e:
            print("error:", e)
            raise e
        finally:
            await solana_client.close()

    async def get_balance(
        self,
        address_obj: Address,
        token_asset: TokenAsset,
    ) -> float:
        try:
            address = address_obj.main
            chain_network = cast(Network, token_asset.network)
            solana_client = await self.get_network_provider(chain_network)

            if token_asset.contractAddress:
                associated_token_account = spl_token.get_associated_token_address(
                    PublicKey(address),
                    WRAPPED_SOL_MINT,
                )

                rpc_resp = await solana_client.get_token_account_balance(
                    associated_token_account
                )
                if "result" not in rpc_resp:
                    raise Exception(rpc_resp["error"])
                balance = float(rpc_resp["result"]["value"]["uiAmount"])
            else:
                resp = await solana_client.get_balance(PublicKey(address))
                balance = float(self.format_num(resp["result"]["value"], "from"))
            resp2 = await solana_client.get_token_accounts_by_owner(
                PublicKey(address),
                TokenAccountOpts(program_id=TOKEN_PROGRAM_ID),
            )
            print(resp2, balance)

            return balance
        finally:
            print("always get here")
            await solana_client.close()

    async def approve_spl_token_delegate(
        self,
        solana_client: AsyncClient,
        sender: Keypair,
        delegate: PublicKey,
        token_account: PublicKey,
        amount: int,
    ) -> RPCResponse:
        appr_spl_del_txn = Transaction().add(
            spl_token.approve(
                spl_token.ApproveParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=token_account,
                    delegate=delegate,
                    owner=sender.public_key,
                    amount=amount,
                )
            )
        )

        resp = await solana_client.send_transaction(appr_spl_del_txn, sender)

        return resp

    async def get_transactions(
        self,
        address: Address,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block: int,
    ) -> list[Any]:
        pass

    async def swap_between_wraps(
        self,
        value: float,
        mnemonic: str,
        token_asset: TokenAsset,
    ) -> str:
        sender = self.get_keypair_from_mnemonic(mnemonic)
        chain_network = cast(Network, token_asset.network)
        solana_client = await self.get_network_provider(chain_network)
        associated_token_account = spl_token.get_associated_token_address(
            sender.public_key, WRAPPED_SOL_MINT
        )
        account = await get_or_create_assoc_token_acc(
            solana_client, sender, sender.public_key, associated_token_account
        )
        txn: Transaction
        if token_asset.contractAddress:
            txn = Transaction().add(
                spl_token.close_account(
                    spl_token.CloseAccountParams(
                        program_id=TOKEN_PROGRAM_ID,
                        account=associated_token_account,
                        dest=sender.public_key,
                        owner=sender.public_key,
                    )
                )
            )

        else:
            amount = int(self.format_num(value, "to"))

            txn = Transaction().add(
                transfer(
                    TransferParams(
                        from_pubkey=sender.public_key,
                        to_pubkey=associated_token_account,
                        lamports=amount,
                    )
                ),
                create_sync_native_instruction(associated_token_account),
            )
            if not account.is_initialized:
                txn.add(
                    spl_token.initialize_account(
                        spl_token.InitializeAccountParams(
                            account=associated_token_account,
                            mint=WRAPPED_SOL_MINT,
                            owner=sender.public_key,
                            program_id=TOKEN_PROGRAM_ID,
                        )
                    ),
                )

        res = await solana_client.send_transaction(txn, sender, recent_blockhash=None)
        return str(res["result"])

    async def get_test_token(self, to_address: str, amount: int) -> list[str]:
        try:
            network = await ModelUtilityService.find_one(Network, {"name": "solanadev"})
            if not network:
                raise Exception("no test network set for solana")
            solana_client = await self.get_network_provider(network)
            txn_hashes: list[str] = []
            for _ in range(amount):
                amount = int(self.format_num(1, "to"))
                resp = await solana_client.request_airdrop(
                    PublicKey(to_address), amount
                )

                transaction_id = resp["result"]
                if transaction_id:
                    txn_hashes + [transaction_id]
            return txn_hashes

        except Exception as e:
            print("error:", e)
            raise e
        finally:
            await solana_client.close()
