from apps.blockchain.interfaces.blockchain_interface import ChainServiceName
from apps.blockchain.services.base_eth_service import BaseEvmService

# from apps.chainstream.interfaces.stream_service_interface import StreamProvider
# from apps.chainstream.services.stream_service import StreamService
from apps.wallet.interfaces.walletasset_interface import Address


class EthereumService(BaseEvmService):
    # streamService = StreamService()

    def __init__(self) -> None:
        super().__init__(ChainServiceName.ETH)

    async def create_address(self, mnemonic: str) -> Address:
        address = await super().create_address(mnemonic)
        # await self.streamService.create_address_stream(
        #     StreamProvider.MORALIS, address.main
        # )
        return address
