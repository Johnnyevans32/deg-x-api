from typing import Any, Optional, cast
from pydantic import BaseModel, Field
import pendulum
from web3 import Web3
from apps.appclient.services.appclient_service import AppClientService, Apps
from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.interfaces.transaction_interface import (
    BlockchainTransaction,
    TxnSource,
    TxnStatus,
    TxnType,
)
from apps.blockchain.services.blockchain_service import BlockchainService
from apps.chainstream.interfaces.stream_service_interface import (
    IStreamService,
    StreamProvider,
)
from apps.notification.slack.services.slack_service import SlackService
from apps.wallet.services.wallet_service import WalletService
from core.depends.get_object_id import PyObjectId
from core.config import settings
from core.utils.request import REQUEST_METHOD, HTTPRepository
from core.utils.utils_service import timed_cache


class ICreateStream(BaseModel):
    webhookUrl: str
    description: str
    tag: str
    tokenAddress: str
    topic0: str
    includeNativeTxs: bool
    abi: Any
    filter: Any
    address: str
    chainIds: list[str]
    streamType: str = Field(alias="type")
    id: str
    status: str
    statusMessage: str


class IBlockData(BaseModel):
    number: str
    hash: str
    timestamp: str


class ITxn(BaseModel):
    hash: str
    gas: str
    gasPrice: str
    nonce: str
    input: str
    transactionIndex: Optional[str]
    fromAddress: str
    toAddress: str
    value: str
    txnType: str = Field(alias="type")
    v: str
    r: str
    s: str
    receiptCumulativeGasUsed: str
    receiptGasUsed: str
    receiptContractAddress: str
    receiptRoot: Any
    receiptStatus: str
    tag: str
    streamId: str
    streamType: str


class IStreamData(BaseModel):
    logs: list[Any]
    txns: list[ITxn]
    txsInternal: list[Any]
    chainId: str
    confirmed: bool
    abis: Any
    block: IBlockData
    retries: int
    erc20Transfers: list[Any]
    erc20Approvals: list[Any]
    nftApprovals: Any
    nftTransfers: list[Any]


class MoralisService(IStreamService):
    appClientService = AppClientService()
    blockchainService = BlockchainService()
    walletService = WalletService()
    slackService = SlackService()

    def __init__(self) -> None:
        client_data = None
        try:
            client_data = self.appClientService.get_client_by_name(Apps.MoralisStream)
        except Exception as e:
            print(e)
        self.base_url = client_data.appUrl if client_data else None
        self.httpRepository = HTTPRepository(
            self.base_url,
            {
                "accept": "application/json",
                "content-type": "application/json",
                "x-api-key": client_data.clientSecret if client_data else None,
            },
        )

    def name(self) -> StreamProvider:
        return StreamProvider.MORALIS

    @timed_cache(1000000, 10)
    async def get_supported_chain_ids(self) -> list[str]:
        blockchains = await self.blockchainService.get_blockchains(
            {
                "registryName": {
                    "$in": [
                        ChainServiceName.BSC.value,
                        ChainServiceName.ETH.value,
                        ChainServiceName.TRON.value,
                        ChainServiceName.AVAX.value,
                        ChainServiceName.MATIC.value,
                    ]
                }
            }
        )
        chain_ids = list(map(lambda chain: chain.id, blockchains))
        networks = await self.blockchainService.get_networks_by_query(
            {"blockchain": {"$in": chain_ids}}
        )
        network_chain_ids = list(
            map(lambda network: cast(str, network.chainId), networks)
        )

        return network_chain_ids

    async def create_address_stream(self, address: str) -> ICreateStream | None:
        try:
            chain_ids = self.get_supported_chain_ids()
            user_walletasset = await self.walletService.get_walletasset_by_query(
                {
                    "$or": [
                        {"address.main": address},
                        {"address.test": address},
                    ],
                    "isDeleted": False,
                }
            )
            payload = {
                "webhookUrl": settings.BASE_URL + "/webhook/moralis-strean",
                "tag": user_walletasset.wallet,
                "includeNativeTxs": True,
                "address": address,
                "chainIds": chain_ids,
                "type": "wallet",
            }
            stream_res = await self.httpRepository.call(
                REQUEST_METHOD.POST, "/streams/evm", ICreateStream, payload
            )
            self.slackService.send_message(
                f">*successfully created stream account on moralis* \n "
                f"*Address:* `{address}`  \n *chains:* `{chain_ids}`",
                "backend",
            )
            return stream_res

        except Exception as e:
            self.slackService.send_message(
                f">*error creating stream account on moralis* \n "
                f"*Address:* `{address}`  \n *error:* `{str(e)}`",
                "backend",
            )
            return None

    async def handle_stream_data(self, payload: IStreamData) -> Any:
        network = await self.blockchainService.get_network_by_query(
            {"chainId": payload.chainId}
        )

        txn_obj = []
        for txn in payload.txns:
            wallet_id = txn.tag
            wallet_asset = await self.walletService.get_walletasset_by_query(
                {
                    "wallet": wallet_id,
                    "isDeleted": False,
                    "blockchain": network.blockchain,
                }
            )
            user_address = BlockchainService.get_address(wallet_asset.address, network)
            txn_type = (
                TxnType.DEBIT if txn.fromAddress == user_address else TxnType.CREDIT
            )
            other_user_address = (
                txn.fromAddress if txn_type == TxnType.CREDIT else txn.toAddress
            )
            other_user_walletasset = await self.walletService.get_walletasset_by_query(
                {
                    "$or": [
                        {"address.main": other_user_address},
                        {"address.test": other_user_address},
                    ],
                    "isDeleted": False,
                    "blockchain": network.blockchain,
                }
            )
            txn_payload = BlockchainTransaction(
                transactionHash=txn.hash,
                fromAddress=txn.fromAddress,
                toAddress=txn.toAddress or txn.receiptContractAddress,
                gasPrice=int(txn.gasPrice),
                blockNumber=int(payload.block.number) or 0,
                gasUsed=int(txn.gas),
                network=cast(PyObjectId, network.id),
                wallet=cast(PyObjectId, wallet_id),
                amount=float(Web3.fromWei(int(txn.value), "ether")),
                status=(
                    TxnStatus.SUCCESS
                    if (txn.receiptStatus == "1")
                    else TxnStatus.FAILED
                ),
                otherUser=other_user_walletasset.user
                if other_user_walletasset
                else None,
                isContractExecution=bool(txn.receiptContractAddress),
                txnType=txn_type,
                user=cast(PyObjectId, wallet_asset.user),
                transactedAt=pendulum.from_timestamp(int(payload.block.timestamp)),
                source=TxnSource.STREAM,
                metaData=txn.dict(by_alias=True),
            ).dict(by_alias=True, exclude_none=True)
            txn_obj.append(txn_payload)

        return txn_obj
