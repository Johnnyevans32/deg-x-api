# -*- coding: utf-8 -*-
from fastapi import Response, status
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from core.utils.response_service import ResponseModel, ResponseService

router = InferringRouter(prefix="/webhook", tags=["Webhook 🐞"])


@cbv(router)
class WebhookController:
    responseService = ResponseService()

    @router.post("/sentry")
    def sentry_webhook(self, res: Response) -> ResponseModel[None]:
        # payload = json.loads(
        #     sentry_payload.json(), object_hook=lambda d: SimpleNamespace(**d)
        # )
        return self.responseService.send_response(
            res, status.HTTP_200_OK, "all good here"
        )
