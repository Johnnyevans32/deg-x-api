from fastapi import status
from starlette.background import BackgroundTask

from apps.featureconfig.interfaces.featureconfig_interface import (
    FeatureConfig,
    FeatureName,
    FeatureStatusUpdateDTO,
)
from apps.notification.slack.services.slack_service import SlackService
from core.utils.custom_exceptions import UnicornException
from core.utils.model_utility_service import ModelUtilityService


class FeatureConfigService:
    slackService = SlackService()

    async def get_feature_by_name(self, name: FeatureName) -> FeatureConfig:
        feature_config = await ModelUtilityService.find_one(
            FeatureConfig, {"name": name}
        )

        if not feature_config:
            return await ModelUtilityService.model_create(
                FeatureConfig,
                FeatureConfig(name=name, isEnabled=False).dict(
                    by_alias=True, exclude_none=True
                ),
            )

        return feature_config

    async def is_feature_enabled(self, name: FeatureName) -> bool:
        feature_config = await self.get_feature_by_name(name)
        return feature_config.isEnabled and not feature_config.isDeleted

    def check_feature_enabled_or_fail(self, name: FeatureName) -> None:
        feature_enabled = self.is_feature_enabled(name)
        if not feature_enabled:
            raise UnicornException(
                status_code=status.HTTP_403_FORBIDDEN,
                message=f"{name} has been temporarily disabled",
            )

    async def update_feature(
        self,
        feature_name: FeatureName,
        feature_status_update_dto: FeatureStatusUpdateDTO,
    ) -> None:

        query = {"name": feature_name, "isDeleted": False}
        record_to_update = {"isEnabled": feature_status_update_dto.status}

        await ModelUtilityService.model_update(FeatureConfig, query, record_to_update)
        BackgroundTask(
            self.slackService.send_formatted_message,
            "Feature status update",
            f"{feature_name} feature status has been updated to "
            f"{feature_status_update_dto.status}",
            "backend",
        )
