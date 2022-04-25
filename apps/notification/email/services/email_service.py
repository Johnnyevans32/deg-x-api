from pathlib import Path
from typing import Union

import emails as emails
from emails.template import JinjaTemplate
from pydantic import EmailStr

from apps.user.interfaces.user_interface import AbstractUser, User
from core.config import settings
from core.utils.helper_service import HelperService


class EmailService:
    def send_template_email(
        self,
        email_to: EmailStr = None,
        subject_template: str = "",
        html_template: str = "",
        environment=None,
    ) -> None:
        if email_to is None:
            raise Exception("email for mail sending cant be null")

        if environment is None:
            environment = {}
        assert settings.EMAILS_ENABLED, "Email is Disabled"
        message = emails.Message(
            subject=JinjaTemplate(subject_template),
            html=JinjaTemplate(html_template),
            mail_from=(settings.EMAILS_FROM_NAME, settings.MAIL_SENDER),
        )
        smtp_options = {
            "host": settings.MAIL_SERVER,
            "port": settings.MAIL_PORT,
            "tls": settings.MAIL_TLS,
            "user": settings.MAIL_USERNAME,
            "password": settings.MAIL_PASSWORD,
        }
        print(smtp_options)
        r = message.send(to=email_to, render=environment, smtp=smtp_options)
        print(email_to, settings.MAIL_SENDER, environment, r)

    def send_verification(self, user: Union[User, AbstractUser]) -> None:
        token = HelperService.generate_confirmation_token(user.email)
        confirm_url = settings.UI_URL + "account/confirm/" + str(token)

        subject = "Verify your email address"
        with open(
            Path(settings.EMAIL_TEMPLATES_DIR) / "verifyaccount.html", encoding="utf-8"
        ) as f:
            template_str = f.read()

        self.send_template_email(
            email_to=user.email,
            subject_template=subject,
            html_template=template_str,
            environment={
                "name": f"{user.name.first} {user.name.last}",
                "link": confirm_url,
                "valid_hours": settings.TOKEN_EXPIRATION_IN_HR,
            },
        )

    def send_forgotten_password_link(self, user: User) -> None:
        token = HelperService.generate_confirmation_token(user.email)
        password_reset_url = settings.UI_URL + "account/update-password/" + str(token)

        subject = "Forgotten your password?"
        with open(
            Path(settings.EMAIL_TEMPLATES_DIR) / "resetpassword.html", encoding="utf-8"
        ) as f:
            template_str = f.read()

        self.send_template_email(
            email_to=user.email,
            subject_template=subject,
            html_template=template_str,
            environment={
                "name": f"{user.name.first} {user.name.last}",
                "link": password_reset_url,
                "valid_hours": settings.TOKEN_EXPIRATION_IN_HR,
            },
        )
