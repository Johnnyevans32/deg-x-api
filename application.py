import os
from typing import Any

import socketio
import uvicorn
from fastapi import FastAPI, Request, Response

# from fastapi.concurrency import run_in_threadpool
from fastapi.exception_handlers import http_exception_handler

from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pymongo import monitoring
from scout_apm.api import Config

# from scout_apm.async_.starlette import ScoutMiddleware
from starlette import status
from starlette.exceptions import ExceptionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# from starlette.middleware import Middleware
from starlette.responses import JSONResponse

from apps.blockchain.interfaces.transaction_interface import BlockchainTransaction
from apps.socket.services.socket_service import sio
from apps.user.interfaces.user_interface import User
from core import urls
from core.config import settings
from core.cron import CronJob
from core.db import client, cursor
from core.db.event_listeners import CommandLogger

# from core.db.populate_core_data import seed_deg_x
# from core.middlewares.sentry import sentry_setup
from core.utils.custom_exceptions import UnicornException, UnicornRequest
from core.utils.loggly import logger
from core.utils.response_service import ResponseService

# from fastapi_socketio import SocketManager


# from fastapi_admin.app import app as admin_app


cronJob = CronJob()
responseService = ResponseService()

# CORS
origins = ["*"]

#  servers=[{"url": settings.base_path}],


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        routes=app.routes,
        terms_of_service="https://twitter.com/degxFi",
        contact={"twitter": "https://twitter.com/degxFi"},
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://api.typedream.com/v0/document/public/2E7bNs9xrG"
        "NYzVd2gtrfgXs9r6l_degx-removebg-preview.png?bucket=document"
    }

    app.openapi_schema = openapi_schema

    return app.openapi_schema


def create_app() -> FastAPI:
    Config.set(
        key="[AVAILABLE IN THE SCOUT UI]",
        name="deg-x-alpha",
        monitor=True,
    )
    # middleware = [
    #     # Should be *first* in your stack, so it's the outermost and can
    #     # track all requests
    #     Middleware(ScoutMiddleware),
    # ]
    openapi_url = "/api/v1/openapi.json" if settings.IS_DEV else None
    app = FastAPI(
        debug=False,
        openapi_url=openapi_url,
    )

    app.logger = logger  # type: ignore[attr-defined]

    # FASTAPI ADMIN
    # app.mount("/admin", admin_app)

    # Set all CORS enabled origins

    if settings.BACKEND_CORS_ORIGINS:
        origins_raw = settings.BACKEND_CORS_ORIGINS.split(",")
        for origin in origins_raw:
            use_origin = origin.strip()
            origins.append(use_origin)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(urls.router, prefix="/api/v1")
    socket_app = socketio.ASGIApp(sio, app)
    app.mount("/socket", socket_app, name="socket")
    app.openapi = lambda: custom_openapi(app)  # type: ignore[assignment]
    app.add_middleware(ExceptionMiddleware, handlers=app.exception_handlers)

    @app.on_event("startup")
    async def startup() -> None:
        logger.info("Setting up model collections")
        monitoring.register(CommandLogger())
        if settings.CRON_ENABLED:
            cronJob.scheduler.start()
        # await seed_deg_x()
        User.init()
        BlockchainTransaction.init()
        # sentry_setup()
        logger.info("Done setting up model collections")

        # run_in_threadpool(mongo_data_streaming)

    @app.on_event("shutdown")
    async def shutdown() -> None:
        logger.info("Closing connection with MongoDB.")
        cursor.close()
        client.close()
        cronJob.scheduler.shutdown()
        logger.info("Closed connection with MongoDB.")

    @app.exception_handler(UnicornException)
    async def unicorn_exception_handler(
        request: UnicornRequest, exc: UnicornException
    ) -> JSONResponse:
        return JSONResponse(
            {"message": exc.message, "data": exc.data},
            status_code=exc.status_code,
        )

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse | Response:
        if exc.status_code in [404, 405, 500]:
            return JSONResponse(
                {
                    "message": responseService.status_code_message[exc.status_code],
                    "data": None,
                },
                status_code=exc.status_code,
            )
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            {
                "message": responseService.status_code_message[
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ],
                "data": [
                    str(error["loc"][-1]) + f": {error['msg']}"
                    for error in exc.errors()
                ],
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return app


_app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = str(os.environ.get("HOST", "0.0.0.0"))
    uvicorn.run(
        "application:_app",
        host=host,
        port=port,
        log_level="info",
        reload=True,
    )
