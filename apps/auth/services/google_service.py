from operator import itemgetter

from google.auth.transport import requests
from google.oauth2 import id_token

from apps.user.interfaces.user_interface import AbstractUser, SignUpMethod, User
from apps.user.services.user_service import UserService
from core.config import settings
from core.utils.helper_service import HelperService


class GoogleService:
    userService = UserService()

    async def verify_oauth_sign_in(self, user_id_token: str) -> dict[str, User]:
        try:
            idinfo = id_token.verify_oauth2_token(user_id_token, requests.Request())
            aud, email, name = itemgetter("aud", "email", "name")(idinfo)
            if aud not in [settings.GOOGLE_CLIENT_ID]:
                raise ValueError("Could not verify audience.")

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            # userid = idinfo.sub
            try:
                user = self.userService.get_user_by_email(email)
            except ValueError:
                first_name, other_name = name.split()
                password = HelperService.hash_password("password")
                user_data = {
                    "firstName": first_name,
                    "lastName": other_name,
                    "email": email,
                    "password": password,
                    "isVerified": True,
                    "signUpMethod": SignUpMethod.google.value,
                }
                user_obj = AbstractUser(**user_data)
                user = self.userService.create_user(user_obj)

            return {"user": user}
        except Exception as e:
            # Invalid token
            print("invalid token", e)
            raise Exception("invalid token")
