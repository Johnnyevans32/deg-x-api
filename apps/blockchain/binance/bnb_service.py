# from typing import Any, Callable, cast

# from mnemonic import Mnemonic
# from apps.blockchain.interfaces.blockchain_interface import ChainServiceName

# from apps.blockchain.interfaces.network_interface import Network, NetworkType
# from apps.blockchain.interfaces.tokenasset_interface import TokenAsset
# from apps.blockchain.types.blockchain_service_interface import IBlockchainService
# from apps.user.interfaces.user_interface import User
# from apps.wallet.interfaces.wallet_interface import Wallet
# from apps.wallet.interfaces.walletasset_interface import Address

# from core.utils.request import HTTPRepository

# from binance_chain.wallet import Wallet as BNBWallet
# from binance_chain.environment import BinanceEnvironment
# from binance_chain.messages import TransferMsg, Signature
# from binance_chain.http import HttpApiClient


# class BnbService(IBlockchainService, HTTPRepository):
#     mnemo = Mnemonic("english")

#     def __init__(self) -> None:
#         self.format_num: Callable[[int | float, str], int | float] = (
#             lambda num, num_type: num * 10 ** 6 if num_type == "to" else num / 10 ** 6
#         )

#     def name(self) -> ChainServiceName:
#         return ChainServiceName.BNB

#     def get_network_provider(self):
#         pass

#     def get_wallet_from_mnemonic(
#         self, mnemonic: str, networkType: NetworkType = NetworkType.TESTNET
#     ) -> BNBWallet:
#         env = (
#             BinanceEnvironment.get_testnet_env()
#             if networkType == NetworkType.TESTNET
#             else BinanceEnvironment.get_production_env()
#         )
#         wallet = BNBWallet.create_wallet_from_mnemonic(
#             mnemonic,
#             env=env,
#         )

#         return wallet

#     async def create_address(self, mnemonic: str) -> Address:
#         # Generate seed from mnemonic
#         test_wallet = self.get_wallet_from_mnemonic(mnemonic)
#         main_wallet = self.get_wallet_from_mnemonic(mnemonic, NetworkType.MAINNET)
#         # Construct from seed
#         return Address(
#             **{
#                 "main": main_wallet.address,
#                 "test": test_wallet.address,
#             }
#         )

#     async def send(
#         self,
#         address_obj: Address,
#         to_address: str,
#         value: float,
#         token_asset: TokenAsset,
#         mnemonic: str,
#         gas=2000000,
#         gas_price="50",
#     ):
#         network = cast(Network, token_asset.network)
#         wallet = self.get_wallet_from_mnemonic(mnemonic, network.networkType)

#         transfer_msg = TransferMsg(
#             wallet=wallet,
#             symbol="BNB",
#             amount=value,
#             to_address=to_address,
#             memo="Thanks for the beer",
#         )
#         signed_msg = Signature(transfer_msg).sign()
#         return signed_msg

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
#         env = (
#             BinanceEnvironment.get_testnet_env()
#             if network.networkType == NetworkType.TESTNET
#             else BinanceEnvironment.get_production_env()
#         )
#         client = HttpApiClient(env=env)
#         balance = client.get_account(address)

#         balance = self.format_num(int(balance), "from")
#         return str(balance)

#     async def get_transactions(
#         self,
#         address: Address,
#         user: User,
#         wallet: Wallet,
#         chain_network: Network,
#         start_block: int,
#     ) -> list[Any]:
#         pass
