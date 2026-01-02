from __future__ import annotations

import allure

import pytest

from framework.retry import RetryableHttpError


pytestmark = pytest.mark.resilience


allure.dynamic.suite("Resilience")

@allure.story("Resilience & retry policy")
@allure.title("QA Platform: Retry on 503 respects attempts")
def test_retry_on_503_respects_attempts(client, cfg, monkeypatch):
    calls = {"n": 0}
    real = client.session.request

    def spy(*args, **kwargs):
        calls["n"] += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(client.session, "request", spy)

    with pytest.raises(RetryableHttpError):
        with allure.step("GET /status/503"):
            client.get("/status/503")

    assert calls["n"] == cfg.retry.attempts, "Should retry exactly configured attempts for retryable status"


@allure.story("Resilience & retry policy")
@allure.title("QA Platform: No retry on 404")
def test_no_retry_on_404(client, monkeypatch):
    calls = {"n": 0}
    real = client.session.request

    def spy(*args, **kwargs):
        calls["n"] += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(client.session, "request", spy)

    with allure.step("GET /status/404"):
        r = client.get("/status/404")
    assert r.status_code == 404
    assert calls["n"] == 1, "404 must not be retried"


@allure.story("Resilience & retry policy")
@allure.title("QA Platform: Retry on 429 respects attempts")
def test_retry_on_429_respects_attempts(client, cfg, monkeypatch):
    calls = {"n": 0}
    real = client.session.request

    def spy(*args, **kwargs):
        calls["n"] += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(client.session, "request", spy)

    with pytest.raises(RetryableHttpError):
        with allure.step("GET /status/429"):
            client.get("/status/429")

    assert calls["n"] == cfg.retry.attempts
