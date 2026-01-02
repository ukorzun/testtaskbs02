from __future__ import annotations

import allure

import pytest

from framework.data_gen import make_user_payload
from framework.metrics import track_test_duration


pytestmark = pytest.mark.smoke


allure.dynamic.suite("Smoke")

@allure.story("Dynamic data")
@allure.title("HTTPBin: Uuid is valid")
def test_uuid_is_valid(api):
    with track_test_duration("test_uuid_is_valid"):
        with allure.step("GET /uuid"):
            data = api.uuid()
        assert str(data.uuid)


@allure.story("Dynamic data")
@allure.title("HTTPBin: Randomized payload roundtrip")
def test_randomized_payload_roundtrip(api):
    user = make_user_payload()
    with track_test_duration("test_randomized_payload_roundtrip"):
        with allure.step("POST /anything (json)"):
            data = api.anything_post_json(user.as_dict())
        assert data.json == user.as_dict()
