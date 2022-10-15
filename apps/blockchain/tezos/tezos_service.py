from typing import Any, Callable, Union, cast

from mnemonic import Mnemonic
from pytezos import pytezos
from pytezos.client import PyTezosClient
from pytezos.crypto.key import Key
from pytezos.operation.group import OperationGroup

from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.interfaces.blockchain_service_interface import IBlockchainService
from apps.blockchain.interfaces.transaction_interface import (
    BlockchainTransaction,
    TxnSource,
    TxnStatus,
    TxnType,
)
from apps.blockchain.tezos.tezos_type import ITezosAccountTxn
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import Address
from core.depends.get_object_id import PyObjectId
from core.utils.model_utility_service import ModelUtilityService
from core.utils.request import REQUEST_METHOD, HTTPRepository
from core.utils.response_service import ResponseModel


class TezosService(IBlockchainService, HTTPRepository):
    httpRepository = HTTPRepository()
    mnemo = Mnemonic("english")

    def __init__(self) -> None:
        self.format_num: Callable[[int | float, str], int | float] = (
            lambda num, num_type: num * 10**6 if num_type == "to" else num / 10**6
        )

    def name(self) -> ChainServiceName:
        return ChainServiceName.XTZ

    @staticmethod
    def get_key_from_mnemonic(mnemonic: str) -> Key:
        key = Key.from_mnemonic(mnemonic)
        return key

    async def create_address(self, mnemonic: str) -> Address:
        # Generate seed from mnemonic
        key = TezosService.get_key_from_mnemonic(mnemonic)
        address = key.public_key_hash()
        return Address(main=address, test=address)

    async def send(
        self,
        from_address: str,
        to_address: str,
        value: float,
        token_asset: TokenAsset,
        mnemonic: str,
        gas: int = 2000000,
        gas_price: int = 50,
    ) -> str:
        network = cast(Network, token_asset.network)
        key = Key.from_mnemonic(mnemonic)
        tez_client: PyTezosClient = pytezos.using(network.providerUrl, key=key)
        amount = int(self.format_num(value, "to"))

        if token_asset.contractAddress:
            # KT1PW3aKxfB89HUrq8ywnw9tLvxtuHLgsjJW
            crt = tez_client.contract(token_asset.contractAddress)
            transfer_op = crt.transfer(
                [
                    {
                        "from_": from_address,
                        "txs": [
                            {
                                "to_": to_address,
                                "token_id": 0,
                                "amount": amount,
                            }
                        ],
                    }
                ]
            ).operation_group
        else:
            transfer_op = tez_client.transaction(destination=to_address, amount=amount)

        txn_res = self.sign_txn(
            network,
            mnemonic,
            transfer_op,
        )
        return txn_res

    def sign_txn(
        self,
        chain_network: Network,
        mnemonic: str,
        transfer_op: OperationGroup,
    ) -> Any:
        txn_res = transfer_op.autofill().sign().inject()
        return txn_res

    async def get_balance(
        self,
        address: str,
        token_asset: TokenAsset,
    ) -> float:
        network = cast(Network, token_asset.network)
        tez_client: PyTezosClient = pytezos.using(shell=network.providerUrl)

        if token_asset.contractAddress:
            tez_crt = pytezos.contract(token_asset.contractAddress)
            balance_res = tez_crt.balance_of(
                requests=[{"owner": address, "token_id": 0}], callback=None
            ).view()

        else:
            balance_res = tez_client.account(address)

        balance = float(self.format_num(int(balance_res["balance"]), "from"))
        return balance

    async def get_transactions(
        self,
        address: str,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block: int,
    ) -> list[Any]:
        assert chain_network.apiExplorer, "network apiexplorer not found"

        res = await self.httpRepository.call(
            REQUEST_METHOD.GET,
            f"{chain_network.apiExplorer.url}/explorer/account/{address}/"
            "operations?limit=100&order=desc",
            ResponseModel[list[ITezosAccountTxn]],
        )

        txns_result = res.data
        assert txns_result, "no tezos transaction"

        txn_obj: list[Any] = []
        for txn in txns_result:
            txn_type = (
                TxnType.DEBIT if txn.sender == address.lower() else TxnType.CREDIT
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
                transactionHash=txn.hash,
                fromAddress=txn.sender,
                toAddress=txn.receiver,
                gasPrice=int(self.format_num(txn.fee, "to")),
                blockNumber=txn.height or 0,
                gasUsed=txn.gas_used,
                blockConfirmations=txn.confirmations or 0,
                network=cast(PyObjectId, chain_network.id),
                wallet=cast(PyObjectId, wallet.id),
                amount=txn.volume,
                status=TxnStatus.SUCCESS if txn.is_success else TxnStatus.FAILED,
                txnType=txn_type,
                user=cast(PyObjectId, user.id),
                tokenasset=tokenasset.id,
                explorerUrl=str(chain_network.blockExplorerUrl) + txn.hash,
                # otherUser=other_user_walletasset.user
                # if other_user_walletasset
                # else None,
                transactedAt=txn.time,
                source=TxnSource.EXPLORER,
                metaData=txn.dict(by_alias=True),
            ).dict(by_alias=True, exclude_none=True)
            txn_obj.append(chain_txn)
        return txn_obj

    async def activate_and_reveal_acc(
        self, tez_client: PyTezosClient, activation_code: str, pkh: str, public_key: str
    ) -> Any:
        activate_op: OperationGroup = tez_client.activate_account(activation_code, pkh)
        activate_res = activate_op.fill().sign().inject()

        reveal_op: OperationGroup = tez_client.reveal(public_key, pkh)
        reveal_res = reveal_op.fill().sign().inject()

        return reveal_res, activate_res

    async def get_test_token(self, to_address: str, amount: float) -> str:
        network = await ModelUtilityService.find_one(Network, {"name": "tezosdev"})
        if not network:
            raise Exception("no test network set for tezos")

        source: dict[str, Union[str, list[str]]] = {
            "pkh": "tz1eidfKmVqfwjmJfz6aGJqbntf5kcurjyRy",
            "mnemonic": [
                "corn",
                "stove",
                "decline",
                "wheel",
                "always",
                "gun",
                "chimney",
                "town",
                "romance",
                "until",
                "cram",
                "wrong",
                "safe",
                "clump",
                "into",
            ],
            "email": "almwbbdj.wfhrrhtk@teztnets.xyz",
            "password": "E4r92Gi2LM",
            "amount": "160891353809",
            "activation_code": "8dfbe56175a6a1fa3db1ebe919984da4d68ed92f",
        }
        key = Key.from_mnemonic(
            source["mnemonic"], str(source["password"]), str(source["email"])
        )
        tez_client: PyTezosClient = pytezos.using(network.providerUrl, key)

        balance_res = tez_client.account(source["pkh"])
        balance = self.format_num(int(balance_res["balance"]), "from")

        if balance < amount:
            raise Exception("insufficient balance")

        transfer_op: OperationGroup = tez_client.transaction(
            destination=to_address, amount=int(self.format_num(amount, "to"))
        )
        txn = transfer_op.fill().sign().inject()
        return txn["hash"]
