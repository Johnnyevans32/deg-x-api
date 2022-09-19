import io
import json
from operator import itemgetter
from typing import Any

# from google.auth.transport import requests
# from google.oauth2 import id_token
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaIoBaseUpload

from apps.auth.interfaces.auth_interface import AuthResponse
from apps.auth.services.jwt_service import JWTService
from apps.cloudplatform.interfaces.cloud_interface import CloudProvider
from apps.cloudplatform.interfaces.cloud_service_interface import ICloudService
from apps.user.interfaces.user_interface import SignUpMethod, User, Name
from apps.user.services.user_service import UserService
from core.utils.loggly import logger
from core.utils.utils_service import NotFoundInRecord


class GoogleService(ICloudService):
    userService = UserService()
    jwtService = JWTService()
    folder_name = "Deg X"

    def name(self) -> CloudProvider:
        return CloudProvider.GOOGLE

    async def oauth_sign_in(self, auth_token: str) -> AuthResponse:
        try:
            creds = Credentials(
                auth_token,
            )
            service: Resource = build("oauth2", "v2", credentials=creds)

            idinfo = service.userinfo().get().execute()
            print("idinfo", idinfo)
            # idinfo = id_token.verify_oauth2_token(creds, requests.Request())
            email, name = itemgetter("email", "name")(idinfo)
            # if aud not in [settings.WEB_GOOGLE_CLIENT_ID]:
            #     raise ValueError("Could not verify audience.")

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            # userid = idinfo.sub

            user = await self.userService.get_user_by_query({"email": email})
            assert user.id, "id is null"
            access_token = self.jwtService.sign_jwt(user.id, "ACCESS_TOKEN")
            refresh_token = self.jwtService.sign_jwt(user.id, "REFRESH_TOKEN")
            await self.userService.create_user_refresh_token(user, refresh_token)
            return AuthResponse(
                user=user,
                accessToken=access_token,
                refreshToken=refresh_token,
            )
        except NotFoundInRecord:
            return await self.oauth_sign_up(auth_token, idinfo)
        except Exception as e:
            # Invalid token
            logger.error(f"Error verifing google auth token - {str(e)}")
            raise Exception(f"Error verifing google auth token - {str(e)}")
        finally:
            service.close()

    async def oauth_sign_up(self, auth_token: str, idinfo: Any = None) -> AuthResponse:
        try:
            if not idinfo:
                creds = Credentials(auth_token)
                service: Resource = build("oauth2", "v2", credentials=creds)

                idinfo = service.userinfo().get().execute()
                # idinfo = id_token.verify_oauth2_token(
                #     creds.id_token, requests.Request()
                # )

            email, name = itemgetter("email", "name")(idinfo)
            # if aud not in [settings.WEB_GOOGLE_CLIENT_ID]:
            #     raise ValueError("Could not verify audience")

            first_name, other_name, *_ = name.split() + [None]
            user_obj = User(
                name=Name(
                    first=first_name,
                    last=other_name,
                ),
                username=email,
                email=email,
                isVerified=True,
                signUpMethod=SignUpMethod.GOOGLE,
            )
            user_res = await self.userService.create_user(user_obj)

            user, wallet, keystore = user_res
            assert user.id, "id is null"
            access_token = self.jwtService.sign_jwt(user.id, "ACCESS_TOKEN")
            refresh_token = self.jwtService.sign_jwt(user.id, "REFRESH_TOKEN")
            await self.userService.create_user_refresh_token(user, refresh_token)
            return AuthResponse(
                user=user,
                wallet=wallet,
                keystore=keystore,
                accessToken=access_token,
                refreshToken=refresh_token,
            )
        except Exception as e:
            # Invalid token
            logger.error(f"Error verifing google auth token - {str(e)}")
            raise Exception(f"Error verifing google auth token - {str(e)}")

    def create_folder(
        self, auth_token: str, folder_name: str, service: Resource = None
    ) -> str:
        """Create a folder
        Returns : Folder Id

        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """
        try:
            if not service:
                creds = Credentials(auth_token)
                service = build("drive", "v3", credentials=creds)
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }

            file = service.files().create(body=file_metadata, fields="id").execute()

        except HttpError as e:
            logger.error(f"Error creating folder - {str(e)}")
            file = None

        return file.get("id", None)

    def get_file_or_folder_id(
        self, auth_token: str, folder_name: str, service: Resource = None
    ) -> str | None:
        """Search file in drive location

        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """

        try:
            if not service:
                creds = Credentials(auth_token)
                service = build("drive", "v3", credentials=creds)
            files = []
            page_token = None
            while True:
                # pylint: disable=maybe-no-member
                response = (
                    service.files()
                    .list(
                        q="mimeType = 'application/vnd.google-apps.folder'"
                        f"and name = '{folder_name}'",
                        spaces="drive",
                        fields="nextPageToken, " "files(id, name)",
                        pageToken=page_token,
                    )
                    .execute()
                )
                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break

        except HttpError as e:
            logger.error(f"Error getting folder - {str(e)}")
        if not files:
            return None
        return files[0].get("id", None)

    def upload_file(self, auth_token: str, file_name: str, data: Any) -> str:
        try:
            creds = Credentials(auth_token)
            service: Resource = build("drive", "v3", credentials=creds)

            # Call the Drive v3 API
            folder = self.get_file_or_folder_id(auth_token, self.folder_name, service)

            if not folder:
                folder = self.create_folder(auth_token, self.folder_name, service)
            file_metadata = {"name": file_name, "parents": [folder]}
            obj = io.StringIO(json.dumps(data))
            media = MediaIoBaseUpload(
                obj,
                mimetype="application/json",
            )
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            return file.get("id")

        except HttpError as e:
            # TODO(developer) - Handle errors from drive API.
            logger.error(f"Error uploading file - {str(e)}")
            raise e
        finally:
            service.close()
