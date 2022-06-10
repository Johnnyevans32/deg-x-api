# -*- coding: utf-8 -*-
from fastapi import Response, status
from fastapi.routing import APIRouter

from apps.featureconfig.interfaces.featureconfig_interface import (
    FeatureName,
    FeatureStatusUpdateDTO,
)
from apps.featureconfig.services.featureconfig_service import FeatureConfigService
from core.utils.custom_exceptions import UnicornRequest
from core.utils.response_service import ResponseService

router = APIRouter(prefix="/api/v1/feature-config", tags=["Feature Config 🌈"])


featureConfigService = FeatureConfigService()
responseService = ResponseService()


@router.get("/check-status/{feature_name}")
async def check_feature_status(
    request: UnicornRequest, response: Response, feature_name: FeatureName
):
    try:
        request.app.logger.info(f"checking enabled status for {feature_name} feature")
        feature_status = featureConfigService.is_feature_enabled(feature_name)
        request.app.logger.info(f"checking enabled status for {feature_name} feature")
        return responseService.send_response(
            response, status.HTTP_200_OK, "feature status retrieved", feature_status
        )

    except Exception as e:
        request.app.logger.error(
            f"Error checking the enabled status of {feature_name} feature - {str(e)}"
        )
        return responseService.send_response(
            response,
            status.HTTP_400_BAD_REQUEST,
            f"Error in getting feature status: {str(e)}",
        )


@router.put("/update-status/{feature_name}")
async def update_feature_status(
    request: UnicornRequest,
    res: Response,
    feature_name: FeatureName,
    feature_status_update_dto: FeatureStatusUpdateDTO,
):
    try:
        request.app.logger.info(f"updating status for {feature_name} feature")
        featureConfigService.update_feature(feature_name, feature_status_update_dto)

        request.app.logger.info(f"done updating status for {feature_name} feature")
        return responseService.send_response(
            res, status.HTTP_200_OK, "feature status updated successfully"
        )
    except Exception as e:
        request.app.logger.error(
            f"Error updating the status of {feature_name} feature - {str(e)}"
        )
        return responseService.send_response(
            res,
            status.HTTP_400_BAD_REQUEST,
            f"Error updating feature status {str(e)}",
        )
