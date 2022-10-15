import random
import string
from typing import Any, Callable, cast

from bitcoinlib.services.services import Service
from bitcoinlib.wallets import Wallet as BitcoinWallet
from mnemonic import Mnemonic

from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.interfaces.network_interface import Network, NetworkType
from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
from apps.blockchain.interfaces.blockchain_service_interface import IBlockchainService
from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.wallet_interface import Wallet
from apps.wallet.interfaces.walletasset_interface import Address
from core.utils.request import HTTPRepository


class BasecoinService(IBlockchainService):
    httpRepository = HTTPRepository()
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
        return Address(
            main=main_wallet.get_key().address, test=test_wallet.get_key().address
        )

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
        address: str,
        token_asset: TokenAsset,
    ) -> float:
        network = cast(Network, token_asset.network)

        balance = Service(
            network=self.network_map[self.coin_network(network.networkType)]
        ).getbalance(address)
        return float(self.format_num(balance, "from"))

    async def get_transactions(
        self,
        address: str,
        user: User,
        wallet: Wallet,
        chain_network: Network,
        start_block: int,
    ) -> list[Any]:
        pass
