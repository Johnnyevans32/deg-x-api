# -*- coding: utf-8 -*-
from typing import Any, Sequence

from fastapi import Depends, Response, status, APIRouter
from fastapi_restful.cbv import cbv

from apps.auth.services.auth_bearer import JWTBearer
from apps.defi.lending.types.lending_types import IReserveToken, IUserAcccountData
from apps.defi.lending.interfaces.lending_request_interface import (
    LendingRequest,
    LendingRequestOut,
)
from apps.defi.lending.services.lending_service import LendingService
from apps.defi.lending.types.lending_types import BaseLendingActionDTO, BorrowAssetDTO
from core.depends.get_object_id import PyObjectId
from core.middleware.encryption import DecrptRequestRoute
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseModel, ResponseService

router = APIRouter(
    prefix="/defi/lending", tags=["Defi 💸"], route_class=DecrptRequestRoute
)


@cbv(router)
class LendingController:
    lendingService = LendingService()
    responseService = ResponseService()

    @router.get(
        "/account-data",
        dependencies=[Depends(JWTBearer())],
    )
    async def get_user_account_data(
        self,
        request: UnicornRequest,
        response: Response,
        defi_provider_id: PyObjectId | None,
    ) -> ResponseModel[IUserAcccountData]:
        try:
            user = request.state.user
            request.app.logger.info(f"getting user lending pool data for - {user.id}")
            user_lending_data = await self.lendingService.get_user_lending_data(
                user, defi_provider_id
            )
            request.app.logger.info("done getting user lending pool data ")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "user lending account data retrieved",
                user_lending_data,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting user lending account data: {str(e)}",
            )

    @router.get(
        "/config",
        dependencies=[Depends(JWTBearer())],
    )
    async def get_user_config(
        self, request: UnicornRequest, response: Response
    ) -> ResponseModel[Any]:
        try:
            user = request.state.user
            request.app.logger.info(f"getting user lending config data for - {user.id}")
            user_lending_data = await self.lendingService.get_user_config(user)
            request.app.logger.info("done getting user lending config data ")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "user lending config data retrieved",
                user_lending_data,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting user lending config data: {str(e)}",
            )

    @router.get(
        "/",
        dependencies=[Depends(JWTBearer())],
    )
    async def get_user_lending_requests(
        self,
        request: UnicornRequest,
        response: Response,
        defi_provider: PyObjectId | None,
        page_num: int = 1,
        page_size: int = 10,
    ) -> ResponseModel[Sequence[LendingRequestOut]]:
        try:
            user = request.state.user
            request.app.logger.info(f"getting user lending requests - {user.id}")
            (
                user_lending_data,
                metadata,
            ) = await self.lendingService.get_user_lending_requests(
                user, page_num, page_size, defi_provider
            )
            request.app.logger.info("done getting user lending requests ")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "user lending requests retrieved",
                user_lending_data,
                metadata,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting user lending requests data: {str(e)}",
            )

    @router.post(
        "/supply",
        dependencies=[Depends(JWTBearer())],
    )
    async def supply_asset(
        self, request: UnicornRequest, response: Response, payload: BaseLendingActionDTO
    ) -> ResponseModel[LendingRequest]:
        try:
            user = request.state.user
            request.app.logger.info(
                f"initiating deposit request to protocol - {user.id}"
            )
            borrow_asset_res = await self.lendingService.supply(user, payload)
            request.app.logger.info("done initiating deposit request to protocol ")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "asset deposit to protocol successfully",
                borrow_asset_res,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in initiating deposit request to protocol: {str(e)}",
            )

    @router.post(
        "/borrow",
        dependencies=[Depends(JWTBearer())],
    )
    async def borrrow_asset(
        self, request: UnicornRequest, response: Response, payload: BorrowAssetDTO
    ) -> ResponseModel[LendingRequest]:
        try:
            user = request.state.user
            request.app.logger.info(
                f"initiating borrow request to protocol - {user.id}"
            )
            borrow_asset_res = await self.lendingService.borrow(user, payload)
            request.app.logger.info("done initiating borrow request to protocol ")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "asset borrowed to wallet successfully",
                borrow_asset_res,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in initiating borrow request to protocol: {str(e)}",
            )

    @router.post(
        "/repay",
        dependencies=[Depends(JWTBearer())],
    )
    async def repay_asset(
        self, request: UnicornRequest, response: Response, payload: BorrowAssetDTO
    ) -> ResponseModel[LendingRequest]:
        try:
            user = request.state.user
            request.app.logger.info(
                f"initiating repaid request to protocol - {user.id}"
            )
            repay_asset_res = await self.lendingService.repay(user, payload)
            request.app.logger.info("done initiating repaid request to protocol ")
            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "asset repaid to protocol successfully",
                repay_asset_res,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in initiating repay request to protocol: {str(e)}",
            )

    @router.get(
        "/reserve-assets",
    )
    async def get_reserve_assets(
        self,
        request: UnicornRequest,
        response: Response,
        defi_provider_id: PyObjectId | None,
    ) -> ResponseModel[list[IReserveToken]]:
        try:
            request.app.logger.info("getting reserve assets from protocol")
            reserved_assets_res = await self.lendingService.get_reserve_assets(
                defi_provider_id
            )
            request.app.logger.info("done getting reserve assets from protocol")

            return self.responseService.send_response(
                response,
                status.HTTP_200_OK,
                "reserve assets retrieved successfully",
                reserved_assets_res,
            )

        except Exception as e:
            return self.responseService.send_response(
                response,
                status.HTTP_400_BAD_REQUEST,
                f"Error in getting reserve assets from protocol: {str(e)}",
            )
