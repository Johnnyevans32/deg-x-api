# -*- coding: utf-8 -*-
from fastapi import Response, status
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from core.utils.response_service import ResponseModel, ResponseService

router = InferringRouter(prefix="/health-check", tags=["Health Check 🩺"])


@cbv(router)
class HealthController:
    responseService = ResponseService()

    @router.get("/")
    def health_check(self, res: Response) -> ResponseModel[None]:
        return self.responseService.send_response(
            res, status.HTTP_200_OK, "all good here, works"
        )
