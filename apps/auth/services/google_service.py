from operator import itemgetter

from google.auth.transport import requests
from google.oauth2 import id_token

from apps.auth.interfaces.auth_interface import AuthResponse
from apps.auth.services.jwt_service import JWTService
from apps.user.interfaces.user_interface import SignUpMethod, User
from apps.user.services.user_service import UserService
from core.config import settings
from core.utils.loggly import logger
from core.utils.utils_service import NotFoundInRecord


class GoogleService:
    userService = UserService()
    jwtService = JWTService()

    async def verify_oauth_sign_in(self, user_id_token: str) -> AuthResponse:
        try:
            idinfo = id_token.verify_oauth2_token(user_id_token, requests.Request())
            aud, email, name = itemgetter("aud", "email", "name")(idinfo)
            if aud not in [settings.WEB_GOOGLE_CLIENT_ID]:
                raise ValueError("Could not verify audience.")

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            # userid = idinfo.sub

            user = await self.userService.get_user_by_query({"email": email})
            assert user.id
            access_token = self.jwtService.sign_jwt(user.id, "ACCESS_TOKEN")
            refresh_token = self.jwtService.sign_jwt(user.id, "REFRESH_TOKEN")
            await self.userService.create_user_refresh_token(user, refresh_token)
            return AuthResponse(
                user=user,
                accessToken=access_token,
                refreshToken=refresh_token,
            )
        except NotFoundInRecord:
            return await self.verify_oauth_sign_up(user_id_token)
        except Exception as e:
            # Invalid token
            logger.error(f"Error verifing google auth token - {str(e)}")
            raise Exception("invalid token")

    async def verify_oauth_sign_up(self, user_id_token: str) -> AuthResponse:
        try:
            idinfo = id_token.verify_oauth2_token(user_id_token, requests.Request())
            aud, email, name = itemgetter("aud", "email", "name")(idinfo)
            if aud not in [settings.WEB_GOOGLE_CLIENT_ID]:
                raise ValueError("Could not verify audience.")

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            # userid = idinfo.sub

            first_name, other_name = name.split()
            user_data = {
                "name": {
                    "firstName": first_name,
                    "lastName": other_name,
                },
                "email": email,
                "isVerified": True,
                "signUpMethod": SignUpMethod.GOOGLE,
            }
            user_obj = User(**user_data)
            user_res = await self.userService.create_user(user_obj)

            user, keystore = user_res
            assert user.id
            access_token = self.jwtService.sign_jwt(user.id, "ACCESS_TOKEN")
            refresh_token = self.jwtService.sign_jwt(user.id, "REFRESH_TOKEN")
            await self.userService.create_user_refresh_token(user, refresh_token)
            return AuthResponse(
                user=user,
                keystore=keystore,
                accessToken=access_token,
                refreshToken=refresh_token,
            )
        except Exception as e:
            # Invalid token
            logger.error(f"Error verifing google auth token - {str(e)}")
            raise Exception("invalid token")
