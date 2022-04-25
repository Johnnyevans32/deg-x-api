# -*- coding: utf-8 -*-
from typing import List

from fastapi import Request, Response, status
from fastapi.routing import APIRouter

from apps.country.interfaces.country_interface import Country
from apps.country.services.country_service import CountryService
from core.utils.response_service import ResponseService, get_response_model


router = APIRouter(prefix="/api/v1/country", tags=["Country 🇺🇸🇳🇬"])


countryService = CountryService()
responseService = ResponseService()


@router.get("", response_model=get_response_model(List[Country], "CountryResponse"))
async def get_countries(
    request: Request,
    response: Response,
    page_num: int = 1,
    page_size: int = 10,
):
    try:
        request.app.logger.info("getting countries")
        res, meta = countryService.get_country(page_num, page_size)
        request.app.logger.info("done getting countries")
        return responseService.send_response(
            response, status.HTTP_200_OK, "countries retrieved", res, meta
        )
    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting countries: {str(e)}",
        )


@router.get(
    "/search",
    response_model=get_response_model(List[Country], "SearchCountryResponse"),
)
async def search_countries(
    request: Request,
    response: Response,
    search_query_name: str,
    page_num: int = 1,
    page_size: int = 10,
):
    try:
        request.app.logger.info("getting countries")
        res, meta = countryService.search_country(
            search_query_name, page_num, page_size
        )
        request.app.logger.info("done getting country")
        return responseService.send_response(
            response, status.HTTP_200_OK, "country matches retrieved", res, meta
        )
    except Exception as e:
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting countries: {str(e)}",
        )
