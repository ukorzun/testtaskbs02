from __future__ import annotations

import allure

import pytest
import requests

from framework.http_client import HttpClient
from framework.config import ServiceConfig, RetryConfig


pytestmark = pytest.mark.resilience


allure.dynamic.suite("Resilience")

@allure.story("Resilience & timeouts")
@allure.title("QA Platform: Timeout is raised and retried")
def test_timeout_is_raised_and_retried(monkeypatch, cfg):
    """QA check: network exceptions (timeouts) are retried and finally surfaced."""
    service = ServiceConfig(base_url=cfg.service.base_url, timeout_s=0.5)
    retry_cfg = RetryConfig(
        attempts=3,
        backoff_s=0.1,
        backoff_multiplier=1.0,
        retry_on_statuses=cfg.retry.retry_on_statuses,
    )
    c = HttpClient(service=service, retry_cfg=retry_cfg)

    calls = {"n": 0}
    real = c.session.request

    def spy(*args, **kwargs):
        calls["n"] += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(c.session, "request", spy)

    with pytest.raises(requests.RequestException):
        with allure.step("GET /delay/3 (timeout)"):
            c.get("/delay/3")

    assert calls["n"] == retry_cfg.attempts
