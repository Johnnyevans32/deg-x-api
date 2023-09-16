# -*- coding: utf-8 -*-
from fastapi import Response, status, APIRouter
from fastapi_restful.cbv import cbv

from apps.marketdata.services.marketdata_service import MarketDataService
from apps.marketdata.services.marketdata_type import IPriceData
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(prefix="/marketdata", tags=["Market data 🌈"])


@cbv(router)
class MarketDataController:
    marketDataService = MarketDataService()
    responseService = ResponseService()

    @router.get("/")
    async def get_historical_price_data(
        self,
        request: UnicornRequest,
        response: Response,
    ) -> ResponseModel[list[IPriceData]]:
        try:
            request.app.logger.info("fetching price data")
            price_data = await self.marketDataService.get_historical_price_data()
            request.app.logger.info("done fetching price data")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "price data fetched successfully",
                price_data,
            )

        except Exception as e:
            request.app.logger.error(f" - {str(e)}")
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in fetching price data: {str(e)}",
            )
