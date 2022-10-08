from typing import Any, cast

from pytezos import pytezos
from pytezos.client import PyTezosClient

from apps.blockchain.interfaces.network_interface import Network
from apps.blockchain.tezos.tezos_service import TezosService
from apps.defi.interfaces.defiprovider_interface import DefiProvider
from apps.defi.lending.aave.aave_interface import IReserveTokens, IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import InterestRateMode
from apps.defi.lending.services.lending_service_interface import ILendingService
from core.utils.request import HTTPRepository
from core.utils.utils_service import timed_cache


class YupanaService(ILendingService):
    tezosService = TezosService()
    httpRepository = HTTPRepository()

    def name(self) -> str:
        return "yupana_service"

    async def get_user_account_data(
        self, user_addr: str, defi_provider: DefiProvider
    ) -> IUserAcccountData:
        pass

    async def get_user_config(self, user_addr: str, defi_provider: DefiProvider) -> Any:
        pass

    async def deposit(
        self,
        asset: str,
        value: float,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        referral_code: int = 0,
        gas: int = 80000,
        gas_price: int = 50,
    ) -> str:
        key = TezosService.get_key_from_mnemonic(mnemonic)
        network = cast(Network, defi_provider.network)
        tez_client: PyTezosClient = pytezos.using(network.providerUrl, key)
        yupana = tez_client.contract(defi_provider.contractAddress)
        # proxy = tez_client.contract("")
        amount = int(self.tezosService.format_num(value, "to"))
        token_id = 1
        txn_group = pytezos.bulk(
            # yupana.updateInterest(token_id),
            # proxy.getPrice([token_id]),
            yupana.mint(token_id, amount, amount),
        )
        txn_res = self.tezosService.sign_txn(network, mnemonic, txn_group)
        print(txn_res)
        return txn_res

    async def withdraw(
        self,
        asset: str,
        value: int,
        to: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        gas: int = 70000,
        gas_price: int = 50,
    ) -> str:
        key = TezosService.get_key_from_mnemonic(mnemonic)
        network = cast(Network, defi_provider.network)
        tez_client: PyTezosClient = pytezos.using(network.providerUrl, key)
        yupana = tez_client.contract(defi_provider.contractAddress)
        proxy = tez_client.contract("")
        # amount of yTokens to burn, pass 0 to burn all.
        amount = int(self.tezosService.format_num(value, "to"))
        borrow_ids = [1, 2]  # user borrowed tokens
        token_id = 1
        borrow_updates = [
            yupana.updateInterest(borrow_token_id) for borrow_token_id in borrow_ids
        ]
        borrow_updates.append(
            proxy.getPrice([borrow_token_id for borrow_token_id in borrow_ids])
        )
        txn_group = pytezos.bulk(
            *borrow_updates,
            yupana.updateInterest(token_id),
            proxy.getPrice([token_id]),
            yupana.redeem(token_id, amount),
        )
        txn_res = self.tezosService.sign_txn(network, mnemonic, txn_group)
        print(txn_res)
        return txn_res

    async def borrow(
        self,
        asset: str,
        value: float,
        interest_rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        referral_code: int = 0,
        gas: int = 70000,
        gas_price: int = 50,
    ) -> str:
        key = TezosService.get_key_from_mnemonic(mnemonic)
        network = cast(Network, defi_provider.network)
        tez_client: PyTezosClient = pytezos.using(network.providerUrl, key)
        yupana = tez_client.contract(defi_provider.contractAddress)
        proxy = tez_client.contract("")
        amount = int(self.tezosService.format_num(value, "to"))
        borrow_ids = [1, 2]  # user borrowed tokens
        token_id = 1
        borrow_updates = [
            yupana.updateInterest(borrow_token_id) for borrow_token_id in borrow_ids
        ]
        borrow_updates.append(
            proxy.getPrice([borrow_token_id for borrow_token_id in borrow_ids])
        )
        txn_group = pytezos.bulk(
            *borrow_updates,
            yupana.updateInterest(token_id),
            proxy.getPrice([token_id]),
            yupana.borrow(token_id, amount),
        )

        txn_res = self.tezosService.sign_txn(network, mnemonic, txn_group)
        print(txn_res)
        return txn_res

    async def repay(
        self,
        asset: str,
        value: float,
        rate_mode: InterestRateMode,
        on_behalf_of: str,
        defi_provider: DefiProvider,
        mnemonic: str,
        gas: int = 40000,
        gas_price: int = 50,
    ) -> str:
        key = TezosService.get_key_from_mnemonic(mnemonic)
        network = cast(Network, defi_provider.network)
        tez_client: PyTezosClient = pytezos.using(network.providerUrl, key)
        yupana = tez_client.contract(defi_provider.contractAddress)
        proxy = tez_client.contract("")
        amount = int(self.tezosService.format_num(value, "to"))
        borrow_ids = [1, 2]  # user borrowed tokens
        token_id = 1
        borrow_updates = [
            yupana.updateInterest(borrow_token_id) for borrow_token_id in borrow_ids
        ]
        borrow_updates.append(
            proxy.getPrice([borrow_token_id for borrow_token_id in borrow_ids])
        )
        txn_group = pytezos.bulk(
            *borrow_updates,
            yupana.updateInterest(token_id),
            proxy.getPrice([token_id]),
            yupana.repay(token_id, amount),
        )
        txn_res = self.tezosService.sign_txn(network, mnemonic, txn_group)
        print(txn_res)
        return txn_res

    async def swap_borrow_rate_mode(
        self,
        asset: str,
        rate_mode: int,
        defi_provider: DefiProvider,
    ) -> Any:
        pass

    async def set_user_use_reserve_as_collateral(
        self,
        asset: str,
        use_as_collateral: bool,
        defi_provider: DefiProvider,
    ) -> Any:
        pass

    @timed_cache(10, 10, asyncFunction=True)
    async def get_reserve_assets(
        self, defi_provider: DefiProvider
    ) -> list[IReserveTokens]:
        pass
