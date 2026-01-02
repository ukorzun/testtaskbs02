from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from framework.retry import retry
from framework.config import RetryConfig, ServiceConfig

logger = logging.getLogger("framework.http_client")


@dataclass
class HttpClient:
    service: ServiceConfig
    retry_cfg: RetryConfig

    def __post_init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "testtaskbs01/0.3"})

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.service.base_url.rstrip('/')}/{path.lstrip('/')}"
        attempts = self.retry_cfg.attempts
        backoff_s = self.retry_cfg.backoff_s
        backoff_multiplier = self.retry_cfg.backoff_multiplier
        statuses = tuple(self.retry_cfg.retry_on_statuses)

        @retry(
            attempts=attempts,
            backoff_s=backoff_s,
            backoff_multiplier=backoff_multiplier,
            retry_on_statuses=statuses,
        )
        def _do() -> requests.Response:
            logger.info("HTTP %s %s", method.upper(), url)

            # Allure attachments (best-effort)
            try:
                from framework.reporting.allure_helpers import attach_request, attach_response  # noqa

                attach_request(
                    method=method,
                    url=url,
                    headers={**self.session.headers, **(kwargs.get("headers") or {})},
                    params=kwargs.get("params"),
                    body=kwargs.get("json") if "json" in kwargs else kwargs.get("data"),
                )
            except Exception:
                pass

            resp = self.session.request(method=method, url=url, timeout=self.service.timeout_s, **kwargs)

            try:
                from framework.reporting.allure_helpers import attach_response  # noqa
                attach_response(resp)
            except Exception:
                pass

            return resp

        return _do()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None, data: Any = None, **kwargs) -> requests.Response:
        return self.request("POST", path, json=json, data=data, **kwargs)
