# -*- coding: utf-8 -*-
from fastapi import Response, status
from fastapi.routing import APIRouter

from apps.appclient.interfaces.appclient_interface import AppClientIn
from apps.appclient.services.appclient_service import AppClientService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService

router = APIRouter(prefix="/api/v1/appclient", tags=["App Client 🌈"])


appClientService = AppClientService()
responseService = ResponseService()


@router.post("/create")
async def create_app_client(
    request: UnicornRequest, response: Response, app_client: AppClientIn
):
    try:
        request.app.logger.info("")
        client_obj = appClientService.create_client(app_client)
        request.app.logger.info("")
        return responseService.send_response(
            response, status.HTTP_200_OK, "app client created", client_obj
        )

    except Exception as e:
        request.app.logger.error(f" - {str(e)}")
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in creating app client: {str(e)}",
        )
