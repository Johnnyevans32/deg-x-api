from functools import partial
from typing import Any

from pymongo import DESCENDING

from apps.blockchain.interfaces.blockchain_interface import Blockchain
from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.interfaces.transaction_interface import BlockchainTransaction
from apps.blockchain.services.blockchain_registry_service import BlockchainRegistry
from apps.notification.slack.services.slack_service import SlackService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import WalletAsset
from core.db import db

# from core.utils.helper_service import timed_cache
from core.utils.loggly import logger
from core.utils.model_utility_service import ModelUtilityService
from core.utils.request import HTTPRepository
from core.utils.response_service import MetaDataModel


class BlockchainService:
    blockchainRegistry = BlockchainRegistry()
    httpRepository = HTTPRepository()
    slackService = SlackService()

    # @timed_cache(10)
    @staticmethod
    def get_blockchains(query: dict) -> list[Blockchain]:
        logger.info("retrieving blockchains")
        blockchains = ModelUtilityService.find(Blockchain, query)

        return blockchains

    @staticmethod
    def get_blockchain_by_query(query: dict) -> Blockchain:
        logger.info("retrieving blockchains")
        blockchain = ModelUtilityService.find_one(Blockchain, query)
        if blockchain is None:
            raise Exception("blockchain not found")
        return blockchain

    @staticmethod
    def get_network_by_query(query: dict) -> Network:
        logger.info("retrieving network chain")
        chain_network = ModelUtilityService.find_one(Network, query)
        if chain_network is None:
            raise Exception("network chain not found")
        return chain_network

    # @timed_cache(10)
    @staticmethod
    def get_token_assets(query: dict) -> list[TokenAsset]:
        logger.info(f"retrieving token assets for query - {query}")
        token_assets = ModelUtilityService.find(TokenAsset, query)

        return token_assets

    @staticmethod
    def get_last_block_txn_by_query(query: dict) -> BlockchainTransaction | None:
        txn_rec = db.blockchaintransaction.find_one(
            query, sort=[("blockNumber", DESCENDING)]
        )

        if txn_rec is None:
            return None

        return BlockchainTransaction(**txn_rec)

    @staticmethod
    def get_token_asset_by_query(query: dict) -> TokenAsset:
        token_asset = ModelUtilityService.find_one(TokenAsset, query)

        if token_asset is None:
            raise Exception("")

        return token_asset

    def update_user_txns(
        self, user: User, user_default_wallet: Wallet, network: Network
    ):
        try:
            blockchain = network.blockchain

            user_asset = ModelUtilityService.find_one(
                WalletAsset,
                {
                    "blockchain": blockchain.id,
                    "wallet": user_default_wallet.id,
                    "isDeleted": False,
                },
            )

            if user_asset is None:
                raise Exception("user asset not found")

            user_last_txn = BlockchainService.get_last_block_txn_by_query(
                {
                    "user": user.id,
                    "network": network.id,
                    "wallet": user_default_wallet.id,
                    "isDeleted": False,
                },
            )
            print("user_last_txn", user_last_txn)
            start_block = 0 if user_last_txn is None else user_last_txn.blockNumber

            default_wallet_txns = self.blockchainRegistry.get_service(
                blockchain.registryName
            ).get_transactions(
                user_asset.address, user, user_default_wallet, network, start_block
            )

            if default_wallet_txns:
                ModelUtilityService.model_create_many(
                    BlockchainTransaction, default_wallet_txns
                )

            return default_wallet_txns
        except Exception as e:
            self.slackService.send_message(
                f">*error updating network txns for user* \n "
                f"*user:* `{user.id}` \n *network:* `{network.name}` \n *error:* `{e}`",
                "backend",
            )

    def create_address(self, blockchain_provider: str, mnemonic: str) -> str:
        return self.blockchainRegistry.get_service(blockchain_provider).create_address(
            mnemonic
        )

    def send(self, user: User, to_address: str):
        pass

    async def get_transactions(
        self,
        user: User,
        page_num: int,
        page_size: int,
    ) -> tuple[list[BlockchainTransaction], MetaDataModel]:
        user_default_wallet = ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )

        if user_default_wallet is None:
            raise Exception("no default wallet set")

        chain_networks = ModelUtilityService.find_and_populate(
            Network,
            {"networkType": user_default_wallet.networkType, "isDeleted": False},
            ["blockchain"],
        )

        # update user txns before returning
        list(
            map(
                partial(self.update_user_txns, user, user_default_wallet),
                chain_networks,
            )
        )

        return ModelUtilityService.paginate_data(
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

    def get_historical_price_data(self):
        api_res = self.httpRepository.call("GET", "", Any)
        return api_res
