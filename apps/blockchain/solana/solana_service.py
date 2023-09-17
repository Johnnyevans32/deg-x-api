from typing import Any, Callable, cast
import pendulum
import spl.token.instructions as spl_token
from mnemonic import Mnemonic
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import RPCResponse
from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID, WRAPPED_SOL_MINT

from apps.blockchain.interfaces.blockchain_interface import Blockchain, ChainServiceName
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.interfaces.transaction_interface import (
    BlockchainTransaction,
    TxnSource,
    TxnStatus,
    TxnType,
)
from apps.blockchain.solana.solana_utils import (
    ISolanaExplorer,
    create_sync_native_instruction,
    get_or_create_assoc_token_acc,
)
from apps.blockchain.interfaces.blockchain_iservice import IBlockchainService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import Address
from core.depends.get_object_id import PyObjectId
from core.utils.model_utility_service import ModelUtilityService
from core.utils.request import REQUEST_METHOD, HTTPRepository


class SolanaService(IBlockchainService):
    httpRepository = HTTPRepository()
    mnemo = Mnemonic("english")

    def __init__(self) -> None:
        self.format_num: Callable[[int | float, str], int | float] = (
            lambda num, num_type: num * 10**9 if num_type == "to" else num / 10**9
        )

    def name(self) -> ChainServiceName:
        return ChainServiceName.SOL

    def get_network_provider(self, network: Network) -> AsyncClient:
        solana_client = AsyncClient(network.providerUrl)
        # res = await solana_client.is_connected()
        return solana_client

    async def create_address(self, mnemonic: str) -> Address:
        keypair = self.get_keypair_from_mnemonic(mnemonic)
        address = str(keypair.public_key)
        return Address(main=address, test=address)

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
        address: str,
        to_address: str,
        value: float,
        token_asset: TokenAsset,
        mnemonic: str,
        gas: int = 2000000,
        gas_price: int = 50,
    ) -> str:
        owner_address = PublicKey(address)
        chain_network = cast(Network, token_asset.network)
        blockchain = cast(Blockchain, token_asset.blockchain)
        amount = int(self.format_num(value, "to"))
        if token_asset.contractAddress:
            from_token_account = spl_token.get_associated_token_address(
                owner_address,
                PublicKey(token_asset.contractAddress),
            )
            to_token_account = spl_token.get_associated_token_address(
                PublicKey(to_address),
                PublicKey(token_asset.contractAddress),
            )
            # acc1 = await get_or_create_assoc_token_acc(
            #     solana_client, sender, sender.public_key, from_token_account
            # )
            # acc2 = await get_or_create_assoc_token_acc(
            #     solana_client, sender, PublicKey(to_address), to_token_account
            # )
            txn = spl_token.transfer(
                spl_token.TransferParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=from_token_account,
                    dest=to_token_account,
                    owner=owner_address,
                    amount=amount,
                )
            )
        else:
            txn = transfer(
                TransferParams(
                    from_pubkey=owner_address,
                    to_pubkey=PublicKey(to_address),
                    lamports=amount,
                )
            )
        txn_build = Transaction().add(txn)
        resp = await self.sign_txn(chain_network, blockchain, mnemonic, txn_build)
        cluster = (
            "?cluster=devnet"
            if chain_network.networkType == NetworkType.TESTNET
            else ""
        )
        return str(resp["result"]) + cluster

    async def sign_txn(
        self,
        network: Network,
        blockchain: Blockchain,
        mnemonic: str,
        txn_build: Transaction,
    ) -> Any:
        client = self.get_network_provider(network)
        sender = self.get_keypair_from_mnemonic(mnemonic)
        resp = await client.send_transaction(txn_build, sender)
        return resp

    async def get_balance(
        self,
        address: str,
        token_asset: TokenAsset,
    ) -> float:
        try:
            chain_network = cast(Network, token_asset.network)
            solana_client = self.get_network_provider(chain_network)

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
            # resp2 = await solana_client.get_token_accounts_by_owner(
            #     PublicKey(address),
            #     TokenAccountOpts(program_id=TOKEN_PROGRAM_ID),
            # )

            return balance
        finally:
            await solana_client.close()

    async def approve_token_delegation(
        self,
        network: Network,
        blockchain: Blockchain,
        mnemonic: str,
        amount: int,
        asset_address: PublicKey,
        spender_address: PublicKey,
    ) -> RPCResponse:
        sender = self.get_keypair_from_mnemonic(mnemonic)
        token_account = spl_token.get_associated_token_address(
            sender.public_key, asset_address
        )
        appr_spl_del_txn = Transaction().add(
            spl_token.approve(
                spl_token.ApproveParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=token_account,
                    delegate=spender_address,
                    owner=sender.public_key,
                    amount=amount,
                )
            )
        )

        resp = await self.sign_txn(network, blockchain, mnemonic, appr_spl_del_txn)

        return resp

    async def swap_between_wraps(
        self,
        value: float,
        mnemonic: str,
        token_asset: TokenAsset,
    ) -> str:
        sender = self.get_keypair_from_mnemonic(mnemonic)
        chain_network = cast(Network, token_asset.network)
        blockchain = cast(Blockchain, token_asset.blockchain)
        solana_client = self.get_network_provider(chain_network)
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

        resp = await self.sign_txn(chain_network, blockchain, mnemonic, txn)
        return str(resp["result"])

    async def get_transactions(
        self,
        address: str,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block: int = 0,
    ) -> list[Any]:
        assert chain_network.apiExplorer, "network apiexplorer not found"
        cluster = (
            "cluster=devnet" if chain_network.networkType == NetworkType.TESTNET else ""
        )
        res = await self.httpRepository.call(
            REQUEST_METHOD.GET,
            f"{chain_network.apiExplorer.url}/account/transaction?address={address}&"
            + cluster,
            ISolanaExplorer,
        )
        txns_result = res.data
        solana_client = self.get_network_provider(chain_network)
        txn_obj: list[Any] = []
        for txn in txns_result:
            from_address = txn.signer[0]
            txn_type = (
                TxnType.DEBIT
                if from_address.lower() == address.lower()
                else TxnType.CREDIT
            )
            txDetails = await solana_client.get_transaction(txn.txHash)

            to_address: str = (
                address
                if txn_type == TxnType.CREDIT
                else txDetails["result"]["transaction"]["message"]["accountKeys"][1]
            )
            value = int(
                txDetails["result"]["meta"]["postBalances"][1]
                - txDetails["result"]["meta"]["preBalances"][1]
            )
            tokenasset = await ModelUtilityService.find_one(
                TokenAsset,
                {
                    "network": chain_network.id,
                    "isDeleted": False,
                },
            )

            assert tokenasset, "token asset not found"
            assert tokenasset.id, "token asset id not found"
            chain_txn = BlockchainTransaction(
                id=None,
                transactionHash=txn.txHash,
                fromAddress=from_address,
                toAddress=to_address,
                gasPrice=txn.fee,
                blockNumber=txn.slot or 0,
                # gasUsed=cast(int, txn.gasUsed),
                # blockConfirmations=int(txn.confirmations or 0),
                network=cast(PyObjectId, chain_network.id),
                wallet=cast(PyObjectId, wallet.id),
                amount=float(self.format_num(value, "from")),
                status=TxnStatus.SUCCESS,
                txnType=txn_type,
                user=cast(PyObjectId, user.id),
                tokenasset=tokenasset.id,
                explorerUrl=f"{str(chain_network.blockExplorerUrl)}{txn.txHash}?{cluster}",
                # otherUser=other_user_walletasset.user
                # if other_user_walletasset
                # else None,
                transactedAt=pendulum.from_timestamp(txn.blockTime),
                source=TxnSource.EXPLORER,
                metaData=txn.dict(by_alias=True),
            ).dict(by_alias=True, exclude_none=True)
            txn_obj.append(chain_txn)

        return txn_obj

    async def get_test_token(self, to_address: str, amount: float) -> str:
        try:
            network = await ModelUtilityService.find_one(Network, {"name": "solanadev"})
            if not network:
                raise Exception("no test network set for solana")
            solana_client = self.get_network_provider(network)

            amount = int(self.format_num(1, "to"))
            resp = await solana_client.request_airdrop(PublicKey(to_address), amount)

            return resp["result"] + "?cluster=devnet"

        finally:
            await solana_client.close()
