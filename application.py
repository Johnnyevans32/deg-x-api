import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pymongo import monitoring
from scout_apm.api import Config
from scout_apm.async_.starlette import ScoutMiddleware
from starlette import status
from starlette.exceptions import ExceptionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware import Middleware
from starlette.responses import JSONResponse

from apps.blockchain.interfaces.transaction_interface import BlockchainTransaction
from apps.user.interfaces.user_interface import User
from core import urls
from core.config import settings
from core.cron import CronJob
from core.db import client
from core.db.event_listeners import CommandLogger

# from core.db.populate_core_data import seed_deg_x
from core.middlewares.sentry import sentry_setup
from core.middlewares.settings import settings_middleware
from core.utils.custom_exceptions import UnicornException, UnicornRequest
from core.utils.loggly import logger
from core.utils.response_service import ResponseService

# from fastapi_admin.app import app as admin_app


cronJob = CronJob()
responseService = ResponseService()

# CORS
origins = ["*"]


def create_app():
    Config.set(
        key="[AVAILABLE IN THE SCOUT UI]",
        name="deg-x-alpha",
        monitor=True,
    )
    middleware = [
        # Should be *first* in your stack, so it's the outermost and can
        # track all requests
        Middleware(ScoutMiddleware),
    ]
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        debug=False,
        openapi_url="/api/v1/openapi.json",
        terms_of_service="https://twitter.com/0xjevan",
        contact={"twitter": "https://twitter.com/0xjevan"},
        middleware=middleware,
    )

    app.logger = logger  # type: ignore
    # app.include_router(CRUDRouter(schema=WalletAsset))

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

    app.include_router(urls.router)

    app.middleware("http")(settings_middleware(app))
    app.add_middleware(ExceptionMiddleware, handlers=app.exception_handlers)

    @app.on_event("startup")
    async def startup():
        logger.info("Setting up model collections")
        monitoring.register(CommandLogger())
        if settings.CRON_ENABLED:
            cronJob.scheduler.start()
        # await seed_deg_x()
        User.init()
        BlockchainTransaction.init()
        sentry_setup()
        logger.info("Done setting up model collections")

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Closing connection with MongoDB.")
        client.close()
        cronJob.scheduler.shutdown()
        logger.info("Closed connection with MongoDB.")

    @app.exception_handler(UnicornException)
    async def unicorn_exception_handler(request: UnicornRequest, exc: UnicornException):
        return JSONResponse(
            {"message": exc.message, "data": exc.data},
            status_code=exc.status_code,
        )

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ):
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
    ):
        return JSONResponse(
            {
                "message": responseService.status_code_message[
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ],
                "data": [
                    error["loc"][-1] + f": {error['msg']}" for error in exc.errors()
                ],
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return app


_app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "application:_app",
        host="127.0.0.1",
        port=port,
        log_level="info",
        reload=True,
    )
