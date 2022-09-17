# from typing import Any, Callable, cast


# from mnemonic import Mnemonic

# # from pycoin.services.blockcypher import BlockcypherProvider
# from bitcoinlib.services.services import Service

# from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
# from apps.blockchain.interfaces.network_interface import Network, NetworkType
# from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
# from apps.blockchain.types.blockchain_service_interface import IBlockchainService
# from apps.user.interfaces.user_interface import User
# from apps.wallet.interfaces.wallet_interface import Wallet
# from apps.wallet.interfaces.walletasset_interface import Address
# from core.utils.request import HTTPRepository

# from pycoin.networks.registry import network_for_netcode
# from pycoin.networks.bitcoinish import Network as CoinNetwork
# from pycoin.key.BIP32Node import BIP32Node
# from pycoin.services import spendables_for_address


# class BaseAltcoinService(IBlockchainService, HTTPRepository):
#     mnemo = Mnemonic("english")

#     network_map = {"XTN": "testnet", "BTC": "bitcoin"}

#     def __init__(
#         self, testnet: str, mainnet: str, service_name: ChainServiceName
#     ) -> None:
#         self.service_name = service_name
#         self.coin_network: Callable[[NetworkType], str] = (
#             lambda network_type: testnet
#             if network_type == NetworkType.TESTNET
#             else mainnet
#         )
#         self.format_num: Callable[[int | float, str], int | float] = (
#             lambda num, num_type: num * 10**7 if num_type == "to" else num / 10**7
#         )

#     def name(self) -> ChainServiceName:
#         return self.service_name

#     def get_network_provider(self):
#         pass

#     def get_wallet_from_mnemonic(
#         self, mnemonic: str, network: NetworkType = NetworkType.TESTNET
#     ) -> BIP32Node:
#         coin_network: CoinNetwork = network_for_netcode(self.coin_network(network))
#         seed = self.mnemo.to_seed(mnemonic)
#         key: BIP32Node = coin_network.keys.bip32_seed(seed)

#         return key

#     async def create_address(self, mnemonic: str) -> Address:
#         test_wallet = self.get_wallet_from_mnemonic(mnemonic)
#         main_wallet = self.get_wallet_from_mnemonic(mnemonic, NetworkType.MAINNET)
#         return Address(
#             **{
#                 "main": main_wallet.address(),
#                 "test": test_wallet.address(),
#             }
#         )

#     async def send(
#         self,
#         from_address: Address,
#         to_address: str,
#         value: float,
#         token_asset: TokenAsset,
#         mnemonic: str,
#         gas=2000000,
#         gas_price="50",
#     ):

#         network = cast(Network, token_asset.network)
#         wallet = self.get_wallet_from_mnemonic(mnemonic)
#         amount = int(self.format_num(value, "to"))
#         coin_symbol = self.coin_network(network.networkType)
#         coin_network: CoinNetwork = network_for_netcode(coin_symbol)
#         spendables = spendables_for_address(wallet.address(), coin_symbol.lower())
#         wifs = [wallet.wif()]
#         print("wifs", wifs, spendables)
#         payables = [(to_address, amount)]
#         tx = coin_network.tx_utils.create_signed_tx(
#             spendables=spendables, payables=payables, wifs=wifs, fee=0
#         )
#         print("jhahs", tx)

#         return tx

#     async def get_balance(
#         self,
#         address_obj: Address,
#         token_asset: TokenAsset,
#     ):

#         network = cast(Network, token_asset.network)
#         address = (
#             address_obj.test
#             if network.networkType == NetworkType.TESTNET
#             else address_obj.main
#         )
#         # print("aghhhhhhh", self.coin_network(network.networkType), address, address_obj)
#         # balance_obj = BlockcypherProvider(
#         #     self.coin_network(network.networkType)
#         # ).get_balance(address)

#         # print(balance_obj)

#         balance = Service(
#             network=self.network_map[self.coin_network(network.networkType)]
#         ).getbalance(address)

#         print("ssss", balance)
#         return str(self.format_num(balance, "from"))

#     async def get_transactions(
#         self,
#         address: Address,
#         user: User,
#         wallet: Wallet,
#         chain_network: Network,
#         start_block: int,
#     ) -> list[Any]:
#         pass
