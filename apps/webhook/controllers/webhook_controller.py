# -*- coding: utf-8 -*-
from fastapi import Response, status, BackgroundTasks
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter
from apps.chainstream.interfaces.stream_service_interface import StreamProvider
from apps.chainstream.moralis.moralis_service import IStreamData
from apps.chainstream.services.stream_service import StreamService

from core.utils.response_service import ResponseModel, ResponseService

router = InferringRouter(prefix="/webhook", tags=["Webhook 🐞"])


@cbv(router)
class WebhookController:
    responseService = ResponseService()
    streamService = StreamService()

    @router.post("/moralis-strean")
    def sentry_webhook(
        self, res: Response, background_tasks: BackgroundTasks, payload: IStreamData
    ) -> ResponseModel[None]:
        background_tasks.add_task(
            self.streamService.handle_stream_data, StreamProvider.MORALIS, payload
        )
        return self.responseService.send_response(res, status.HTTP_200_OK, "processing")
