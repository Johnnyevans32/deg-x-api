from typing import Any, cast

from pymongo import DESCENDING

from apps.blockchain.interfaces.blockchain_interface import Blockchain, ChainServiceName
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.interfaces.transaction_interface import BlockchainTransaction

from apps.blockchain.registry.blockchain_registry_service import BlockchainRegistry
from apps.notification.slack.services.slack_service import SlackService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import Address, WalletAsset
from apps.blockchain.types.blockchain_type import (
    SendTokenDTO,
    SendTxnRes,
    GetTokenBalance,
    GetTestTokenDTO,
    BalanceRes,
    SwapTokenDTO,
    ReceipientType,
)
from core.db import db
from core.utils.loggly import logger
from core.utils.model_utility_service import ModelUtilityService
from core.utils.request import HTTPRepository
from core.utils.response_service import MetaDataModel
from core.depends.get_object_id import PyObjectId
from core.utils.utils_service import NotFoundInRecord


class BlockchainService:
    blockchainRegistry = BlockchainRegistry()
    httpRepository = HTTPRepository()
    slackService = SlackService()

    @staticmethod
    async def get_blockchains(query: dict[str, Any]) -> list[Blockchain]:
        logger.info("retrieving blockchains")
        blockchains = await ModelUtilityService.find(Blockchain, query)

        return blockchains

    @staticmethod
    async def get_blockchain_by_query(query: dict[str, Any]) -> Blockchain:
        logger.info("retrieving blockchains")
        blockchain = await ModelUtilityService.find_one(Blockchain, query)
        if not blockchain:
            raise Exception("blockchain not found")

        return blockchain

    @staticmethod
    async def get_network_by_query(query: dict[str, Any]) -> Network:
        logger.info("retrieving network chain")
        chain_network = await ModelUtilityService.find_one(Network, query)
        if not chain_network:
            raise Exception("network chain not found")

        return chain_network

    @staticmethod
    async def get_networks_by_query(query: dict[str, Any]) -> list[Network]:
        logger.info("retrieving network chain")
        chain_networks = await ModelUtilityService.find(Network, query)
        if not chain_networks:
            raise Exception("network chains not found")

        return chain_networks

    # @timed_cache(10, 10)
    @staticmethod
    async def get_token_assets(query: dict[str, Any]) -> list[TokenAsset]:
        logger.info(f"retrieving token assets for query - {query}")
        token_assets = await ModelUtilityService.find(TokenAsset, query)

        return token_assets

    @staticmethod
    def get_address(address: Address, network: Network) -> str:
        return (
            address.main if network.networkType == NetworkType.TESTNET else address.test
        )

    @staticmethod
    async def get_last_block_txn_by_query(
        query: dict[str, Any]
    ) -> BlockchainTransaction | None:
        txn_rec = db.blockchaintransaction.find_one(
            query, sort=[("blockNumber", DESCENDING)]
        )

        return BlockchainTransaction(**txn_rec) if txn_rec else None

    @staticmethod
    async def get_token_asset_by_query(query: dict[str, Any]) -> TokenAsset:
        token_asset = await ModelUtilityService.find_one(TokenAsset, query)
        if not token_asset:
            raise Exception("token asset not found")

        return token_asset

    async def create_address(
        self, blockchain_provider: ChainServiceName, mnemonic: str
    ) -> Address:
        return await self.blockchainRegistry.get_service(
            blockchain_provider
        ).create_address(mnemonic)

    async def get_user_wallet_data(
        self,
        wallet_asset: PyObjectId,
    ) -> tuple[Wallet, WalletAsset, Blockchain, TokenAsset]:
        user_asset = await ModelUtilityService.find_one_and_populate(
            WalletAsset,
            {"_id": wallet_asset, "isDeleted": False},
            ["blockchain", "tokenasset", "wallet"],
        )
        if not user_asset:
            raise Exception("user asset not found")

        blockchain = cast(Blockchain, user_asset.blockchain)
        user_wallet = cast(Wallet, user_asset.wallet)
        tokenasset = cast(TokenAsset, user_asset.tokenasset)

        token_asset = await ModelUtilityService.find_one_and_populate(
            TokenAsset,
            {"_id": tokenasset.id, "isDeleted": False},
            [
                "network",
            ],
        )
        if not token_asset:
            raise Exception("token asset not found")

        return user_wallet, user_asset, blockchain, token_asset

    async def get_user_by_query(self, query: dict[str, Any]) -> User:
        user = await ModelUtilityService.find_one(User, query)
        if not user:
            raise NotFoundInRecord(message="user not found")
        return user

    async def verify_mnemonic_and_fail(
        self,
        blockchain_provider: ChainServiceName,
        mnemonic: str,
        user_asset: WalletAsset,
    ) -> None:
        generated_address = await self.create_address(blockchain_provider, mnemonic)

        if user_asset.address.main != generated_address.main:
            raise Exception("wallet mnemonic mismatch")

    async def get_receipient_address(
        self, username: str, blockchain: Blockchain, network: Network
    ) -> str:
        user = await self.get_user_by_query({"username": username})
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        if not user_default_wallet:
            raise Exception("no default wallet set")

        user_asset = await ModelUtilityService.find_one(
            WalletAsset,
            {
                "blockchain": blockchain.id,
                "wallet": user_default_wallet.id,
                "isDeleted": False,
            },
        )
        if not user_asset:
            raise Exception("user asset not found")

        return (
            user_asset.address.main
            if network.networkType == NetworkType.MAINNET
            else user_asset.address.test
        )

    async def send(self, user: User, payload: SendTokenDTO) -> SendTxnRes:
        (
            user_wallet,
            user_asset,
            blockchain,
            token_asset,
        ) = await self.get_user_wallet_data(payload.walletasset)

        network = cast(Network, token_asset.network)

        match payload.receipientType:
            case ReceipientType.ADDRESS:
                receipient = payload.receipient
            case ReceipientType.USERNAME:
                receipient = await self.get_receipient_address(
                    payload.receipient, blockchain, network
                )
            case _:
                pass

        if not receipient:
            raise Exception("receipient not set")

        send_txn = await self.blockchainRegistry.get_service(
            blockchain.registryName
        ).send(
            user_asset.address,
            receipient,
            payload.amount,
            token_asset,
            user_wallet.mnemonic or payload.mnemonic,
        )
        txn_url = str(network.blockExplorerUrl) + send_txn
        return SendTxnRes(transactionHash=txn_url)

    async def get_balance(self, user: User, payload: GetTokenBalance) -> BalanceRes:
        (
            _,
            user_asset,
            blockchain,
            token_asset,
        ) = await self.get_user_wallet_data(payload.walletasset)

        asset_balance = await self.blockchainRegistry.get_service(
            blockchain.registryName
        ).get_balance(
            user_asset.address,
            token_asset,
        )

        return BalanceRes(
            symbol=token_asset.symbol,
            balance=asset_balance,
        )

    async def update_user_txns(
        self, user: User, user_default_wallet: Wallet, network: Network
    ) -> Any:
        try:
            blockchain = cast(Blockchain, network.blockchain)

            user_asset = await ModelUtilityService.find_one(
                WalletAsset,
                {
                    "blockchain": blockchain.id,
                    "wallet": user_default_wallet.id,
                    "isDeleted": False,
                },
            )
            if not user_asset:
                raise Exception("user asset not found")

            user_last_txn = await BlockchainService.get_last_block_txn_by_query(
                {
                    "user": user.id,
                    "network": network.id,
                    "wallet": user_default_wallet.id,
                    "isDeleted": False,
                },
            )
            start_block = user_last_txn.blockNumber if user_last_txn else 0

            default_wallet_txns = await self.blockchainRegistry.get_service(
                blockchain.registryName
            ).get_transactions(
                user_asset.address, user, user_default_wallet, network, start_block
            )
            if default_wallet_txns:
                await ModelUtilityService.model_create_many(
                    BlockchainTransaction, default_wallet_txns
                )

            return default_wallet_txns
        except Exception as e:
            self.slackService.send_message(
                f">*error updating network txns for user* \n "
                f"*user:* `{user.id}` \n *network:* `{network.name}` \n *error:* `{e}`",
                "backend",
            )

    async def get_transactions(
        self,
        user: User,
        page_num: int,
        page_size: int,
    ) -> tuple[list[BlockchainTransaction], MetaDataModel]:
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        if not user_default_wallet:
            raise Exception("no default wallet set")

        chain_networks = await ModelUtilityService.find_and_populate(
            Network,
            {
                "networkType": user_default_wallet.networkType,
                "isDeleted": False,
                "isDefault": True,
            },
            ["blockchain"],
        )

        # update user txns before returning
        chain_ids = []
        for network in chain_networks:
            chain_ids.append(network.id)
            await self.update_user_txns(user, user_default_wallet, network)

        res, meta = await ModelUtilityService.paginate_data(
            BlockchainTransaction,
            {
                "user": user.id,
                "wallet": user_default_wallet.id,
                "network": {"$in": chain_ids},
                "isDeleted": False,
            },
            page_num,
            page_size,
            "transactedAt",
        )

        return res, meta

    async def get_test_token(self, user: User, payload: GetTestTokenDTO) -> SendTxnRes:
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        if not user_default_wallet:
            raise Exception("no default wallet set")

        token_asset = await ModelUtilityService.find_one_and_populate(
            TokenAsset,
            {"symbol": payload.asset, "hasTestToken": True, "isDeleted": False},
            ["blockchain", "network"],
        )
        if not token_asset:
            raise Exception("token symbol not recongized")

        blockchain = cast(Blockchain, token_asset.blockchain)
        network = cast(Network, token_asset.network)
        user_asset = await ModelUtilityService.find_one(
            WalletAsset,
            {
                "blockchain": blockchain.id,
                "wallet": user_default_wallet.id,
                "isDeleted": False,
            },
        )
        if not user_asset:
            raise Exception("user asset not found")

        txn_res = await self.blockchainRegistry.get_service(
            blockchain.registryName
        ).get_test_token(
            user_asset.address.main,
            payload.amount,
        )

        txn_url = str(network.blockExplorerUrl) + txn_res
        return SendTxnRes(transactionHash=txn_url)

    async def swap_between_wraps(self, user: User, payload: SwapTokenDTO) -> str:
        (
            user_wallet,
            _,
            blockchain,
            token_asset,
        ) = await self.get_user_wallet_data(payload.walletasset)

        swap_txn = await self.blockchainRegistry.get_service(
            blockchain.registryName
        ).swap_between_wraps(
            payload.amount,
            user_wallet.mnemonic or payload.mnemonic,
            token_asset,
        )

        return swap_txn
