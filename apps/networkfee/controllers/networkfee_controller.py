# -*- coding: utf-8 -*-

from fastapi import Response, status
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from apps.networkfee.owlracle.owlracle_type import IGasSpeed

from apps.networkfee.services.networkfee_service import (
    NetworkFeeService,
)
from apps.networkfee.types.networkfee_type import TxnSpeedOption
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = InferringRouter(prefix="/network-fee", tags=["Gas station info 🌈"])


@cbv(router)
class NetworkFeeController:
    networkFeeService = NetworkFeeService()
    responseService = ResponseService()

    @router.get("/")
    async def get_network_fee(
        self, request: UnicornRequest, response: Response, network: str
    ) -> ResponseModel[dict[TxnSpeedOption, IGasSpeed]]:
        try:
            request.app.logger.info("retrieving network fee for txn")
            fee_data = await self.networkFeeService.get_network_fee_data(network, True)
            request.app.logger.info("retrieved network fee for txn")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "network fee data retrieved",
                fee_data,
            )

        except Exception as e:
            request.app.logger.error(f"Error retrieving network fee for txn - {str(e)}")
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in retrieving network fee for txn: {str(e)}",
            )
