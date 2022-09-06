# -*- coding: utf-8 -*-
import json
from types import SimpleNamespace
from unittest import TestCase

# import pytest
from httpx import AsyncClient
from pydantic import EmailStr

from application import _app as app
from apps.user.services.user_service import UserService

# from async_asgi_testclient import TestClient

client = AsyncClient(app=app)


# @pytest.mark.asyncio
# async def test_create_post(client: TestClient):
#     resp = await client.post("/posts")

#     assert resp.status_code == 201


class TestAuthModule(TestCase):
    userService = UserService()
    test_email = EmailStr("evans@demigod.com")

    # @pytest.mark.anyio
    # @classmethod
    # async def setUpClass(cls) -> None:
    #     await cls.userService.hard_del_user(cls.test_email)

    async def test_register_user_with_no_payload(self) -> None:
        response = await client.post("/api/v1/account/register")
        assert response.status_code == 422

    async def test_register_user_for_creation(self) -> None:
        test_user_payload = {
            "firstName": "evans",
            "lastName": "demigod",
            "email": self.test_email,
            "password": "password",
            "username": "sss",
            "country": "61689fc4dc4f8ba4c07f52e2",
        }
        response = await client.post("/api/v1/account/register", data=test_user_payload)
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 201
        assert not payload_response.data.user.isVerified

    async def test_register_user_for_dub_username(self) -> None:
        test_user_payload = {
            "firstName": "evans",
            "lastName": "demigod",
            "email": self.test_email,
            "password": "password",
            "username": "sss",
            "country": "61689fc4dc4f8ba4c07f52e2",
        }
        response = await client.post("/api/v1/account/register", data=test_user_payload)
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 400
        assert (
            payload_response.message
            == "User Registration Failed: username already exist"
        )

    async def test_register_user_for_dub_email(self) -> None:
        test_user_payload = {
            "firstName": "evans",
            "lastName": "demigod",
            "email": self.test_email,
            "password": "password",
            "username": "900",
            "country": "61689fc4dc4f8ba4c07f52e2",
        }
        response = await client.post("/api/v1/account/register", data=test_user_payload)
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 409
        assert payload_response.message == f"User with {self.test_email} already exist"

    async def test_login_user_for_not_verified(self) -> None:
        test_user_payload = {
            "email": self.test_email,
            "password": "password",
        }
        response = await client.post("/api/v1/account/login", data=test_user_payload)
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 400
        assert payload_response.message == "User Login Failed: user not verified"

    async def test_login_user_for_success(self) -> None:
        await self.userService.verify_email(self.test_email)
        test_user_payload = {
            "email": self.test_email,
            "password": "password",
        }
        response = await client.post("/api/v1/account/login", data=test_user_payload)
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 200
        assert payload_response.data.token

    # @classmethod
    # async def tearDownClass(cls) -> None:
    #     test_user_payload = {
    #         "firstName": "evans",
    #         "lastName": "demigod",
    #         "email": cls.test_email,
    #         "password": "password",
    #         "username": "sss",
    #         "country": "61689fc4dc4f8ba4c07f52e2",
    #     }
    #     await client.post("/api/v1/account/register", data=test_user_payload)
