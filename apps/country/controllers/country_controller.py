# -*- coding: utf-8 -*-
from fastapi import Response, status, APIRouter
from fastapi_restful.cbv import cbv

from apps.country.interfaces.country_interface import Country
from apps.country.services.country_service import CountryService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(prefix="/country", tags=["Country 🇳🇬"])


@cbv(router)
class CountryController:
    countryService = CountryService()
    responseService = ResponseService()

    @router.get(
        "",
        response_model_by_alias=False,
    )
    async def get_countries(
        self,
        request: UnicornRequest,
        response: Response,
        page_num: int = 1,
        page_size: int = 10,
    ) -> ResponseModel[list[Country]]:
        try:
            request.app.logger.info("getting countries")
            res, meta = await self.countryService.get_country(page_num, page_size)
            request.app.logger.info("done getting countries")
            return self.responseService.send_response(
                response, status.HTTP_200_OK, "countries retrieved", res, meta
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting countries: {str(e)}",
            )

    @router.get(
        "/search",
        response_model_by_alias=False,
    )
    async def search_countries(
        self,
        request: UnicornRequest,
        response: Response,
        search_query_name: str,
        page_num: int = 1,
        page_size: int = 10,
    ) -> ResponseModel[list[Country]]:
        try:
            request.app.logger.info("getting countries")
            res, meta = await self.countryService.search_country(
                search_query_name, page_num, page_size
            )
            request.app.logger.info("done getting country")
            return self.responseService.send_response(
                response, status.HTTP_200_OK, "country matches retrieved", res, meta
            )
        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting countries: {str(e)}",
            )
