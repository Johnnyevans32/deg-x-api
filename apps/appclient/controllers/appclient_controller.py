# -*- coding: utf-8 -*-
from fastapi import Response, status
from fastapi.routing import APIRouter

from apps.appclient.interfaces.appclient_interface import AppClient
from apps.appclient.services.appclient_service import AppClientService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService

router = APIRouter(prefix="/api/v1/appclient", tags=["App Client 🌈"])


appClientService = AppClientService()
responseService = ResponseService()


@router.post("/create")
async def create_app_client(
    request: UnicornRequest, response: Response, app_client: AppClient
):
    try:
        request.app.logger.info(f"creating application client - {app_client}")
        client_obj = await appClientService.create_client(app_client)
        request.app.logger.info("done creating application client")
        return responseService.send_response(
            response, status.HTTP_201_CREATED, "app client created", client_obj
        )

    except Exception as e:
        request.app.logger.error(f" - {str(e)}")
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in creating app client: {str(e)}",
        )
