from __future__ import annotations

import functools
import logging
import time
from typing import Callable, Iterable, Optional, Type

import requests

from framework.metrics import inc_retry


logger = logging.getLogger("framework.retry")


class RetryableHttpError(Exception):
    """Raised when HTTP status code is retryable."""

    def __init__(self, status_code: int, url: str, body_preview: str = "") -> None:
        super().__init__(f"Retryable HTTP {status_code} for {url}. Body preview: {body_preview[:200]}")
        self.status_code = status_code
        self.url = url


def retry(
    *,
    attempts: int,
    backoff_s: float,
    backoff_multiplier: float,
    retry_on_statuses: Iterable[int] = (429, 500, 502, 503, 504),
    retry_on_exceptions: tuple[Type[BaseException], ...] = (requests.RequestException, RetryableHttpError),
) -> Callable:
    """Custom retry decorator with attempt-by-attempt logging.

    - Retries on network exceptions (requests.RequestException by default)
    - Retries on configured HTTP statuses by raising RetryableHttpError
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            delay = backoff_s
            last_exc: Optional[BaseException] = None
            for attempt in range(1, attempts + 1):
                t0 = time.perf_counter()
                try:
                    resp = fn(*args, **kwargs)

                    # If function returns a Response, enforce retryable status codes.
                    if isinstance(resp, requests.Response) and resp.status_code in set(retry_on_statuses):
                        body_preview = ""
                        try:
                            body_preview = resp.text
                        except Exception:
                            body_preview = "<unreadable>"
                        raise RetryableHttpError(resp.status_code, resp.url, body_preview)

                    dt_ms = (time.perf_counter() - t0) * 1000
                    logger.info("Attempt %s/%s succeeded in %.1f ms", attempt, attempts, dt_ms)
                    return resp
                except retry_on_exceptions as exc:
                    dt_ms = (time.perf_counter() - t0) * 1000
                    last_exc = exc
                    if attempt >= attempts:
                        logger.error("Attempt %s/%s failed in %.1f ms (giving up): %s", attempt, attempts, dt_ms, exc)
                        raise
                    # Count retry attempts (excluding the first attempt).
                    inc_retry(n=1)
                    logger.warning(
                        "Attempt %s/%s failed in %.1f ms: %s | next retry in %.2f s",
                        attempt,
                        attempts,
                        dt_ms,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= backoff_multiplier
            # Defensive
            if last_exc:
                raise last_exc
            raise RuntimeError("retry wrapper reached unreachable state")

        return wrapper

    return decorator
