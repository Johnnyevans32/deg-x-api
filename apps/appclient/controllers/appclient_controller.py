# -*- coding: utf-8 -*-
from fastapi import Response, status, APIRouter
from fastapi_restful.cbv import cbv

from apps.appclient.interfaces.appclient_interface import AppClient
from apps.appclient.services.appclient_service import AppClientService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(prefix="/clients", tags=["App Client 🌈"])


@cbv(router)
class AppClientController:
    appClientService = AppClientService()
    responseService = ResponseService()

    @router.post("/")
    async def create_app_client(
        self,
        request: UnicornRequest,
        response: Response,
        app_client: AppClient,
    ) -> ResponseModel[AppClient]:
        try:
            request.app.logger.info(f"creating application client - {app_client}")
            client_obj = await self.appClientService.create_client(app_client)
            request.app.logger.info("done creating application client")
            return self.responseService.send_response(
                response, status.HTTP_201_CREATED, "app client created", client_obj
            )

        except Exception as e:
            request.app.logger.error(f" - {str(e)}")
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in creating app client: {str(e)}",
            )
