# from pathlib import Path

from typing import Any

import emails as emails
from emails.template import JinjaTemplate
from pydantic import EmailStr

from apps.user.interfaces.user_interface import User
from core.config import settings
from core.utils.utils_service import Utils

from ...slack.services.slack_service import SlackService


class EmailService:
    slackService = SlackService()
    email_sigx = """
        <span style="color:red">
            If you didn't make this request you can disregard this email.
        </span> <br><br>
        <a href="https://degx.typedream.app/">
            <img src="https://i.ibb.co/vd7H65L/degx-removebg-preview.png"
             alt="degx" width="40" height="40" border="0">
        </a><br>
        <span>©2022 deg x</span><br>
        <span style="color:#A9A9A9">bringing defi to africa...</span>
    """
    serializer_expiration_in_hr = settings.SERIALIZER_TOKEN_EXPIRATION_IN_SEC / (
        60 * 60
    )

    def send_template_email(
        self,
        email_to: EmailStr = None,
        subject_template: str = "",
        html_template: str = "",
        environment: dict[str, Any] = None,
    ) -> None:
        assert settings.EMAILS_ENABLED, "Email is Disabled"
        if not email_to:
            raise Exception("email for mail sending cant be null")

        if not environment:
            environment = {}
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
        res = message.send(to=email_to, render=environment, smtp=smtp_options)

        print(email_to, settings.MAIL_SENDER, environment, res)

    def send_verification(self, user: User) -> None:
        try:
            token = Utils.generate_confirmation_token(user.email)
            confirm_url = settings.UI_URL + "account/confirm/" + str(token)

            subject = "Welcome!!!"
            html = (
                """
                Hi {{ name }}  👋🏽 <br><br>

                Please kindly confirm your email address by clicking the link
                 below so we can get you started on Deg X: <br>
                <a href="{{ link }}">link</a> <br> The verification of account link will
                expire in {{ valid_hours }} hour(s). <br><br>
            """
                + self.email_sigx
            )

            self.send_template_email(
                email_to=user.email,
                subject_template=subject,
                html_template=html,
                environment={
                    "name": f"{user.name.first} {user.name.last}",
                    "link": confirm_url,
                    "valid_hours": int(self.serializer_expiration_in_hr),
                },
            )
        except Exception as e:
            self.slackService.send_formatted_message(
                "Error sending verification email",
                f"*User:* {user.id} \n *Error:* {e}",
            )

    def send_forgotten_password_link(self, user: User) -> None:
        try:
            token = Utils.generate_confirmation_token(user.email)
            password_reset_url = (
                settings.UI_URL + "/account/update-password/" + str(token)
            )

            subject = "Forgotten your password?"
            # with open(
            #     Path(settings.EMAIL_TEMPLATES_DIR) / "resetpassword.html", encoding="utf-8"
            # ) as f:
            #     template_str = f.read()

            html = (
                """
                Hi {{ name }}  👋🏽  <br><br>

                We received a request to recover your password,
                reset your password by clicking the link below: <br>
                <a href="{{ link }}">link</a> <br>
                The reset password link will expire in {{ valid_hours }} hour(s).
                 <br><br>
            """
                + self.email_sigx
            )
            self.send_template_email(
                email_to=user.email,
                subject_template=subject,
                html_template=html,
                environment={
                    "name": f"{user.name.first} {user.name.last}",
                    "link": password_reset_url,
                    "valid_hours": int(self.serializer_expiration_in_hr),
                },
            )
        except Exception as e:
            self.slackService.send_formatted_message(
                "Error sending forgotten password email",
                f"*User:* {user.id} \n *Error:* {e}",
            )
