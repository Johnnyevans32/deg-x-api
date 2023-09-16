# -*- coding: utf-8 -*-
from fastapi import Response, status, APIRouter
from fastapi_restful.cbv import cbv

from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(prefix="/health-check", tags=["Health Check 🩺"])


@cbv(router)
class HealthController:
    responseService = ResponseService()

    @router.get("/")
    def health_check(self, res: Response) -> ResponseModel[None]:
        return self.responseService.send_response(
            res, status.HTTP_200_OK, "all good here, works"
        )
