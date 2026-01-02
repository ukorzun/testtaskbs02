from __future__ import annotations

import allure

import pytest

from framework.metrics import track_test_duration


pytestmark = pytest.mark.data


allure.dynamic.suite("Data")

@allure.story("Data boundaries")
@allure.title("QA Data: Query params special chars")
def test_query_params_special_chars(api):
    params = {
        "space": "a b",
        "unicode": "Zażółć gęślą jaźń",
        "reserved": "!*'();:@&=+$,/?#[]",
    }
    with allure.step("GET /anything"):
        r = api.anything_get(params=params)
    assert r.status_code == 200
    data = r.json()
    assert data["args"]["space"] == params["space"]
    assert data["args"]["unicode"] == params["unicode"]
    assert data["args"]["reserved"] == params["reserved"]


@allure.story("Data boundaries")
@allure.title("QA Data: Large json payload roundtrip")
def test_large_json_payload_roundtrip(api):
    big = "x" * (256 * 1024)  # 256KB
    payload = {"blob": big}
    with track_test_duration("test_large_json_payload_roundtrip"):
        with allure.step("POST /anything (json)"):
            data = api.anything_post_json(payload)
        assert data.json == payload
