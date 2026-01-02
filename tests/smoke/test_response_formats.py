from __future__ import annotations

import pytest
import allure

from framework.metrics import track_test_duration


pytestmark = pytest.mark.smoke


allure.dynamic.suite("Smoke")

@allure.story("Response formats")
@allure.title("HTTPBin: /anything reflects Accept header (echo) and returns JSON")
@pytest.mark.parametrize("accept", [
    "application/json",
    "text/html",
    "application/xml",
])
def test_anything_reflects_accept_header(api, accept):
    with track_test_duration("test_anything_reflects_accept_header"):
        with allure.step("GET /anything with Accept header"):
            r = api.anything_get(accept=accept)
        assert r.status_code == 200
        assert "application/json" in r.headers.get("Content-Type", "")
        with allure.step("Assert Accept header is echoed back"):
            data = r.json()
            assert data["headers"].get("Accept") == accept


@allure.story("Response formats")
@allure.title("HTTPBin: /html returns text/html")
def test_html_endpoint_returns_html(client):
    with track_test_duration("test_html_endpoint_returns_html"):
        with allure.step("GET /html"):
            r = client.get("/html", headers={"Accept": "text/html"})
        assert r.status_code == 200
        assert "text/html" in r.headers.get("Content-Type", "")
        assert "<html" in r.text.lower()
