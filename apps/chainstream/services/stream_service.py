from typing import Any
from apps.blockchain.interfaces.transaction_interface import BlockchainTransaction
from apps.chainstream.interfaces.stream_service_interface import StreamProvider
from apps.chainstream.services.stream_registry import StreamRegistry
from core.utils.model_utility_service import ModelUtilityService


class StreamService:
    streamRegistry = StreamRegistry()

    async def create_address_stream(
        self,
        provider: StreamProvider,
        address: str,
    ) -> Any:
        stream_service = self.streamRegistry.get_service(provider)

        return await stream_service.create_address_stream(
            address,
        )

    async def handle_stream_data(self, provider: StreamProvider, payload: Any) -> Any:
        stream_service = self.streamRegistry.get_service(provider)

        txn_data = await stream_service.handle_stream_data(payload)
        await ModelUtilityService.model_create_many(BlockchainTransaction, txn_data)
