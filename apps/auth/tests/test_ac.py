# -*- coding: utf-8 -*-
import json
from types import SimpleNamespace
from unittest import TestCase

from fastapi.testclient import TestClient
from pydantic import EmailStr

from application import _app as app
from apps.user.services.user_service import UserService

client = TestClient(app)


class TestAuthModule(TestCase):
    userService = UserService()
    test_email = EmailStr("evans@demigod.com")

    @classmethod
    def setUpClass(cls) -> None:
        cls.userService.hard_del_user(cls.test_email)

    def test_register_user_with_no_payload(self) -> None:
        response = client.post("/api/v1/account/register")
        assert response.status_code == 422

    def test_register_user_for_creation(self) -> None:
        test_user_payload = {
            "firstName": "evans",
            "lastName": "demigod",
            "email": self.test_email,
            "password": "password",
            "username": "sss",
            "country": "61689fc4dc4f8ba4c07f52e2",
        }
        response = client.post(
            "/api/v1/account/register", data=json.dumps(test_user_payload)
        )
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 201
        assert payload_response.data.user.isVerified is False

    def test_register_user_for_dub_username(self) -> None:
        test_user_payload = {
            "firstName": "evans",
            "lastName": "demigod",
            "email": self.test_email,
            "password": "password",
            "username": "sss",
            "country": "61689fc4dc4f8ba4c07f52e2",
        }
        response = client.post(
            "/api/v1/account/register", data=json.dumps(test_user_payload)
        )
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 400
        assert (
            payload_response.message
            == "User Registration Failed: username already exist"
        )

    def test_register_user_for_dub_email(self) -> None:
        test_user_payload = {
            "firstName": "evans",
            "lastName": "demigod",
            "email": self.test_email,
            "password": "password",
            "username": "900",
            "country": "61689fc4dc4f8ba4c07f52e2",
        }
        response = client.post(
            "/api/v1/account/register", data=json.dumps(test_user_payload)
        )
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 409
        assert payload_response.message == f"User with {self.test_email} already exist"

    def test_login_user_for_not_verified(self) -> None:
        test_user_payload = {
            "email": self.test_email,
            "password": "password",
        }
        response = client.post(
            "/api/v1/account/login", data=json.dumps(test_user_payload)
        )
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 400
        assert payload_response.message == "User Login Failed: user not verified"

    def test_login_user_for_success(self) -> None:
        self.userService.verify_email(self.test_email)
        test_user_payload = {
            "email": self.test_email,
            "password": "password",
        }
        response = client.post(
            "/api/v1/account/login", data=json.dumps(test_user_payload)
        )
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 200
        assert payload_response.data.token is not None

    @classmethod
    def tearDownClass(cls) -> None:
        test_user_payload = {
            "firstName": "evans",
            "lastName": "demigod",
            "email": cls.test_email,
            "password": "password",
            "username": "sss",
            "country": "61689fc4dc4f8ba4c07f52e2",
        }
        client.post("/api/v1/account/register", data=json.dumps(test_user_payload))
