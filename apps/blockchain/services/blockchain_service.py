from typing import Any, cast

from pydantic import BaseModel
from pymongo import DESCENDING

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.interfaces.transaction_interface import BlockchainTransaction
from apps.blockchain.registry.blockchain_registry_service import (
    BlockchainRegistry,
    ChainServiceName,
)
from apps.notification.slack.services.slack_service import SlackService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import Address, WalletAsset
from core.db import db
from core.utils.loggly import logger
from core.utils.model_utility_service import ModelUtilityService
from core.utils.request import HTTPRepository
from core.utils.response_service import MetaDataModel


class GetTokenBalance(BaseModel):
    tokenSymbol: str


class SendTokenDTO(GetTokenBalance):
    toAddress: str
    amount: float


class SwapTokenDTO(GetTokenBalance):
    amount: float


class BlockchainService:
    blockchainRegistry = BlockchainRegistry()
    httpRepository = HTTPRepository()
    slackService = SlackService()

    @staticmethod
    async def get_blockchains(query: dict) -> list[Blockchain]:
        logger.info("retrieving blockchains")
        blockchains = await ModelUtilityService.find(Blockchain, query)

        return blockchains

    @staticmethod
    async def get_blockchain_by_query(query: dict) -> Blockchain:
        logger.info("retrieving blockchains")
        blockchain = await ModelUtilityService.find_one(Blockchain, query)
        if not blockchain:
            raise Exception("blockchain not found")

        return blockchain

    @staticmethod
    async def get_network_by_query(query: dict) -> Network:
        logger.info("retrieving network chain")
        chain_network = await ModelUtilityService.find_one(Network, query)
        if not chain_network:
            raise Exception("network chain not found")

        return chain_network

    # @timed_cache(10, 10)
    @staticmethod
    async def get_token_assets(query: dict) -> list[TokenAsset]:
        logger.info(f"retrieving token assets for query - {query}")
        token_assets = await ModelUtilityService.find(TokenAsset, query)

        return token_assets

    @staticmethod
    async def get_last_block_txn_by_query(query: dict) -> BlockchainTransaction | None:
        txn_rec = db.blockchaintransaction.find_one(
            query, sort=[("blockNumber", DESCENDING)]
        )

        return BlockchainTransaction(**txn_rec) if txn_rec else None

    @staticmethod
    async def get_token_asset_by_query(query: dict) -> TokenAsset:
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

    async def send(self, user: User, payload: SendTokenDTO):
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        if not user_default_wallet:
            raise Exception("no default wallet set")

        token_asset = await ModelUtilityService.find_one_and_populate(
            TokenAsset,
            {"symbol": payload.tokenSymbol, "isDeleted": False},
            ["blockchain", "network"],
        )
        if not token_asset:
            raise Exception("token symbol not recongized")

        blockchain = cast(Blockchain, token_asset.blockchain)

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

        send_txn = await self.blockchainRegistry.get_service(
            blockchain.registryName
        ).send(
            user_asset.address,
            payload.toAddress,
            payload.amount,
            token_asset,
            user_default_wallet.mnemonic,
        )
        return {"transactionHash": send_txn}

    async def get_balance(self, user: User, payload: GetTokenBalance):
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        if not user_default_wallet:
            raise Exception("no default wallet set")

        token_asset = await ModelUtilityService.find_one_and_populate(
            TokenAsset,
            {"symbol": payload.tokenSymbol, "isDeleted": False},
            ["blockchain", "network"],
        )
        if not token_asset:
            raise Exception("token symbol not recongized")

        blockchain = cast(Blockchain, token_asset.blockchain)

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

        asset_balance = await self.blockchainRegistry.get_service(
            blockchain.registryName
        ).get_balance(
            user_asset.address,
            token_asset,
        )

        return {
            "symbol": payload.tokenSymbol,
            "balance": asset_balance,
        }

    async def update_user_txns(
        self, user: User, user_default_wallet: Wallet, network: Network
    ):
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
            {"networkType": user_default_wallet.networkType, "isDeleted": False},
            ["blockchain"],
        )

        # update user txns before returning

        for network in chain_networks:
            await self.update_user_txns(user, user_default_wallet, network)

        res, meta = await ModelUtilityService.paginate_data(
            BlockchainTransaction,
            {
                "user": user.id,
                "wallet": user_default_wallet.id,
                "network": {"$in": [network.id for network in chain_networks]},
                "isDeleted": False,
            },
            page_num,
            page_size,
        )

        return res, meta

    async def swap_between_wraps(self, user: User, payload: SwapTokenDTO):
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        if not user_default_wallet:
            raise Exception("no default wallet set")

        token_asset = await ModelUtilityService.find_one_and_populate(
            TokenAsset,
            {"symbol": payload.tokenSymbol, "isDeleted": False},
            ["blockchain", "network"],
        )
        if not token_asset:
            raise Exception("token symbol not recongized")

        blockchain = cast(Blockchain, token_asset.blockchain)

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

        swap_txn = await self.blockchainRegistry.get_service(
            blockchain.registryName
        ).swap_between_wraps(payload.amount, user_default_wallet.mnemonic, token_asset)

        return swap_txn

    async def get_historical_price_data(self):
        api_res = await self.httpRepository.call("GET", "", Any, {"": ""})
        return api_res
