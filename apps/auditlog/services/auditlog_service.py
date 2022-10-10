from apps.socket.services.socket_service import SocketEvent, emit_event_to_clients
from apps.user.interfaces.user_interface import User
from apps.auditlog.interfaces.notification_interface import (
    Notification,
    NotificationType,
)
from apps.notification.slack.services.slack_service import SlackService
from core.utils.model_utility_service import ModelUtilityService
from core.utils.response_service import MetaDataModel


class AuditLogService:
    slackService = SlackService()

    async def create_notification(
        self,
        title: str,
        message: str,
        type: NotificationType = NotificationType.Generic,
        user: User = None,
    ) -> Notification:
        notf_obj = await ModelUtilityService.model_create(
            Notification,
            Notification(title=title, message=message, type=type, user=user).dict(
                by_alias=True, exclude_none=True
            ),
        )
        await emit_event_to_clients(
            SocketEvent.NOTIFICATION,
            notf_obj.title,
            str(user.id) if user else None,
        )

        return notf_obj

    async def get_users_notification(
        self, user: User, page_num: int, page_size: int
    ) -> tuple[list[Notification], MetaDataModel]:
        res, meta_data = await ModelUtilityService.paginate_data(
            Notification,
            {
                "isDeleted": False,
                "$or": [{"user": user.id}, {"type": NotificationType.Generic}],
            },
            page_num,
            page_size,
        )

        return res, meta_data
