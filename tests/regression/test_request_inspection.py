from __future__ import annotations

import allure

import pytest

from framework.data_gen import rand_string, rand_int
from framework.metrics import track_test_duration


pytestmark = pytest.mark.regression


allure.dynamic.suite("Regression")

@allure.story("Request inspection")
@allure.title("HTTPBin: Query params are reflected")
def test_query_params_are_reflected(api):
    token = rand_string(12, 18)
    n = str(rand_int(1, 9999))
    with track_test_duration("test_query_params_are_reflected"):
        with allure.step("GET /anything"):
            r = api.anything_get(params={"token": token, "n": n})
        assert r.status_code == 200
        data = r.json()
        assert data["args"]["token"] == token
        assert data["args"]["n"] == n


@allure.story("Request inspection")
@allure.title("HTTPBin: Headers are reflected")
def test_headers_are_reflected(api):
    trace_id = rand_string(16, 24)
    with track_test_duration("test_headers_are_reflected"):
        with allure.step("GET /anything"):
            r = api.anything_get(headers={"X-Trace-Id": trace_id})
        assert r.status_code == 200
        data = r.json()
        assert data["headers"].get("X-Trace-Id") == trace_id


@allure.story("Request inspection")
@allure.title("HTTPBin: Form data is reflected")
def test_form_data_is_reflected(api):
    with track_test_duration("test_form_data_is_reflected"):
        with allure.step("POST /anything (form)"):
            data = api.anything_post_form({"a": "1", "b": "2"})
        assert data.form == {"a": "1", "b": "2"}
