import random
import string
from typing import Any, Callable, cast

from bitcoinlib.services.services import Service
from bitcoinlib.wallets import Wallet as BitcoinWallet
from mnemonic import Mnemonic

from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.types.blockchain_service_interface import IBlockchainService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import Address
from core.utils.request import HTTPRepository


class BasecoinService(IBlockchainService, HTTPRepository):
    mnemo = Mnemonic("english")
    network_map = {
        "XTN": "testnet",
        "BTC": "bitcoin",
        "XDT": "dogecoin_testnet",
        "DOGE": "dogecoin",
        "XLT": "litecoin_testnet",
        "LTC": "litecoin",
        "tDASH": "dash_testnet",
        "DASH": "dash",
    }

    def __init__(
        self, testnet: str, mainnet: str, service_name: ChainServiceName
    ) -> None:
        self.format_num: Callable[[int | float, str], int | float] = (
            lambda num, num_type: num * 10**7 if num_type == "to" else num / 10**7
        )
        self.coin_network: Callable[[NetworkType], str] = (
            lambda network_type: testnet
            if network_type == NetworkType.TESTNET
            else mainnet
        )
        self.service_name = service_name

    def name(self) -> ChainServiceName:
        return self.service_name

    def get_network_provider(self):
        pass

    def get_wallet_from_mnemonic(
        self, mnemonic: str, network: NetworkType = NetworkType.TESTNET
    ) -> BitcoinWallet:
        wallet_name = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        wallet = BitcoinWallet.create(
            wallet_name,
            keys=mnemonic,
            network=self.network_map[self.coin_network(network)],
        )

        return wallet

    async def create_address(self, mnemonic: str) -> Address:
        test_wallet = self.get_wallet_from_mnemonic(mnemonic)
        main_wallet = self.get_wallet_from_mnemonic(mnemonic, NetworkType.MAINNET)
        # Construct from seed
        print(test_wallet.addresslist(), main_wallet.get_key())
        return Address(
            **{
                "main": main_wallet.get_key().address,
                "test": test_wallet.get_key().address,
            }
        )

    async def send(
        self,
        from_address: Address,
        to_address: str,
        value: float,
        token_asset: TokenAsset,
        mnemonic: str,
        gas=2000000,
        gas_price="50",
    ):
        network = cast(Network, token_asset.network)
        wallet = self.get_wallet_from_mnemonic(mnemonic)
        amount = int(self.format_num(value, "to"))

        hash = wallet.send_to(
            to_address,
            amount,
            network=self.network_map[self.coin_network(network.networkType)],
        )
        return hash

    async def get_balance(
        self,
        address_obj: Address,
        token_asset: TokenAsset,
    ):
        network = cast(Network, token_asset.network)

        address = (
            address_obj.test
            if network.networkType == NetworkType.TESTNET
            else address_obj.main
        )

        balance = Service(
            network=self.network_map[self.coin_network(network.networkType)]
        ).getbalance(address)
        print(balance)
        return str(self.format_num(balance, "from"))

    async def get_transactions(
        self,
        address: Address,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block: int,
    ) -> list[Any]:
        pass
