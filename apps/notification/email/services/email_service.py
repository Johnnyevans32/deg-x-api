# from pathlib import Path

import emails as emails
from emails.template import JinjaTemplate
from pydantic import EmailStr

from apps.user.interfaces.user_interface import User
from core.config import settings
from core.utils.utils_service import Utils


class EmailService:
    serializer_expiration_in_hr = settings.SERIALIZER_TOKEN_EXPIRATION_IN_SEC / (
        60 * 60
    )

    def send_template_email(
        self,
        email_to: EmailStr = None,
        subject_template: str = "",
        html_template: str = "",
        environment=None,
    ) -> None:
        if not email_to:
            raise Exception("email for mail sending cant be null")

        if not environment:
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

    def send_verification(self, user: User) -> None:
        token = Utils.generate_confirmation_token(user.email)
        confirm_url = settings.UI_URL + "account/confirm/" + str(token)

        subject = "Verify your email address"
        html = """
            Hi {{ name }}  👋🏽 <br><br>

            Please kindly confirm your email address so we
            can verify your account by clicking the link below: <br>
            {{ link }} <br> The verification of account link / button will
            expire in {{ valid_hours }} hours. <br><br>

            <span>©2021 deg x</span> <br>
            <span style="color:#A9A9A9">bringing defi to africa </span> <br>
            If you didn't request an account registration you can disregard this email.
        """

        self.send_template_email(
            email_to=user.email,
            subject_template=subject,
            html_template=html,
            environment={
                "name": f"{user.name.first} {user.name.last}",
                "link": confirm_url,
                "valid_hours": self.serializer_expiration_in_hr,
            },
        )

    def send_forgotten_password_link(self, user: User) -> None:
        token = Utils.generate_confirmation_token(user.email)
        password_reset_url = settings.UI_URL + "account/update-password/" + str(token)

        subject = "Forgotten your password?"
        # with open(
        #     Path(settings.EMAIL_TEMPLATES_DIR) / "resetpassword.html", encoding="utf-8"
        # ) as f:
        #     template_str = f.read()

        html = """
            Hi {{ name }}  👋🏽  <br><br>

            We received a request to recover your password,
            reset your password by clicking the link below: <br>
            {{ link }} <br>
            The reset password link / button will expire in {{valid_hours }} hours.  <br><br>

            <span>©2021 deg x</span><br><br>
            <span style="color:#A9A9A9">bringing defi to africa </span> <br>
            If you didn't request a password recovery you can disregard this email.
        """
        self.send_template_email(
            email_to=user.email,
            subject_template=subject,
            html_template=html,
            environment={
                "name": f"{user.name.first} {user.name.last}",
                "link": password_reset_url,
                "valid_hours": self.serializer_expiration_in_hr,
            },
        )
