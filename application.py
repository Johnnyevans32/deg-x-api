import uvicorn
from fastapi import FastAPI, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from pymongo import monitoring
from starlette.exceptions import ExceptionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from apps.user.interfaces.user_interface import User
from apps.wallet.interfaces.walletasset_interface import WalletAsset
from core import urls
from core.config import settings
from core.cron import CronJob
from core.db import client
from core.db.event_listeners import CommandLogger
from core.middlewares.sentry import sentry_setup
from core.middlewares.settings import settings_middleware
from core.utils.loggly import logger
from core.utils.response_service import ResponseService

# from fastapi_admin.app import app as admin_app


cronJob = CronJob()
responseService = ResponseService()
MONGO_URI = settings.DATABASE["URI"]

# CORS
origins = ["*"]


def create_app():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        debug=False,
        openapi_url="/api/v1/openapi.json",
        terms_of_service="https://twitter.com/0xjevan",
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
        User.init()
        sentry_setup()
        logger.info("Done setting up model collections")

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Closing connection with MongoDB.")
        client.close()
        cronJob.scheduler.shutdown()
        logger.info("Closed connection with MongoDB.")

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ):
        if exc.status_code == 404:
            return JSONResponse(
                {"message": responseService.status_code_message[404]}, status_code=404
            )
        if exc.status_code == 405:
            return JSONResponse(
                {"message": responseService.status_code_message[405]}, status_code=405
            )

        if exc.status_code == 500:
            return JSONResponse(
                {"message": responseService.status_code_message[500]}, status_code=500
            )
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return await request_validation_exception_handler(request, exc)

    return app


_app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "application:_app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=True,
    )
