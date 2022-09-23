from typing import Any, cast

from pydantic import BaseModel
from pymongo import DESCENDING

from apps.blockchain.interfaces.blockchain_interface import Blockchain, ChainServiceName
from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.interfaces.transaction_interface import BlockchainTransaction
from apps.blockchain.registry.blockchain_registry_service import BlockchainRegistry
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
    asset: str


class BaseTxnSendDTO(BaseModel):
    amount: float
    mnemonic: str


class SendTokenDTO(GetTokenBalance, BaseTxnSendDTO):
    receipient: str


class SwapTokenDTO(GetTokenBalance, BaseTxnSendDTO):
    pass


class SendTxnRes(BaseModel):
    transactionHash: str


class BalanceRes(BaseModel):
    symbol: str
    balance: float


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

    # @timed_cache(10, 10)
    @staticmethod
    async def get_token_assets(query: dict[str, Any]) -> list[TokenAsset]:
        logger.info(f"retrieving token assets for query - {query}")
        token_assets = await ModelUtilityService.find(TokenAsset, query)

        return token_assets

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

    async def verify_mnemonic_and_fail(
        self,
        blockchain_provider: ChainServiceName,
        mnemonic: str,
        user_asset: WalletAsset,
    ) -> None:
        generated_address = await self.create_address(blockchain_provider, mnemonic)

        if user_asset.address.main != generated_address.main:
            raise Exception("wallet mnemonic mismatch ")

    async def send(self, user: User, payload: SendTokenDTO) -> SendTxnRes:
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        if not user_default_wallet:
            raise Exception("no default wallet set")

        token_asset = await ModelUtilityService.find_one_and_populate(
            TokenAsset,
            {"symbol": payload.asset, "isDeleted": False},
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

        await self.verify_mnemonic_and_fail(
            blockchain.registryName, payload.mnemonic, user_asset
        )

        send_txn = await self.blockchainRegistry.get_service(
            blockchain.registryName
        ).send(
            user_asset.address,
            payload.receipient,
            payload.amount,
            token_asset,
            user_default_wallet.mnemonic or payload.mnemonic,
        )
        return SendTxnRes(transactionHash=send_txn)

    async def get_balance(self, user: User, payload: GetTokenBalance) -> BalanceRes:
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        if not user_default_wallet:
            raise Exception("no default wallet set")

        token_asset = await ModelUtilityService.find_one_and_populate(
            TokenAsset,
            {"symbol": payload.asset, "isDeleted": False},
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

        return BalanceRes(
            symbol=payload.asset,
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

    async def swap_between_wraps(self, user: User, payload: SwapTokenDTO) -> str:
        user_default_wallet = await ModelUtilityService.find_one(
            Wallet, {"user": user.id, "isDeleted": False, "isDefault": True}
        )
        if not user_default_wallet:
            raise Exception("no default wallet set")

        token_asset = await ModelUtilityService.find_one_and_populate(
            TokenAsset,
            {"symbol": payload.asset, "isDeleted": False},
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
        ).swap_between_wraps(
            payload.amount,
            user_default_wallet.mnemonic or payload.mnemonic,
            token_asset,
        )

        return swap_txn
