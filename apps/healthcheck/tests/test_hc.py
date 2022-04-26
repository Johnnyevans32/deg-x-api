# -*- coding: utf-8 -*-
import json
from types import SimpleNamespace
from unittest import TestCase

from fastapi.testclient import TestClient

from application import _app as app

client = TestClient(app)


class TestHealthCheckModule(TestCase):
    def test_health_check(self):
        response = client.get("/api/v1/health-check")
        payload_response = json.loads(
            json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d)
        )
        assert response.status_code == 200
        # assert payload_response.message == "all good here"
