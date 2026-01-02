from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional

from prometheus_client import CollectorRegistry, Counter, Histogram, push_to_gateway, pushadd_to_gateway


REGISTRY = CollectorRegistry()

# Populated by an autouse pytest fixture to allow framework code (e.g. retry)
# to attribute metrics to the currently running test.
CURRENT_TEST_NAME: ContextVar[str] = ContextVar("CURRENT_TEST_NAME", default="unknown")

RETRY_COUNTER = Counter(
    "test_retries_total",
    "Total number of retry attempts executed (excluding the first attempt).",
    ["test_name"],
    registry=REGISTRY,
)

TEST_DURATION = Histogram(
    "test_duration_seconds",
    "Test duration in seconds.",
    ["test_name"],
    registry=REGISTRY,
)


@contextmanager
def track_test_duration(test_name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        TEST_DURATION.labels(test_name=test_name).observe(time.perf_counter() - start)


def set_current_test_name(name: str) -> None:
    CURRENT_TEST_NAME.set(name)


def get_current_test_name() -> str:
    return CURRENT_TEST_NAME.get()


def inc_retry(test_name: Optional[str] = None, n: int = 1) -> None:
    if n <= 0:
        return
    name = test_name or get_current_test_name()
    RETRY_COUNTER.labels(test_name=name).inc(n)


def push_metrics(
    pushgateway_url: str,
    job_name: str,
    grouping_key: Optional[dict] = None,
    *,
    mode: str = "add",
) -> None:
    """Push collected metrics to Pushgateway.

    mode:
      - "add": accumulate metrics in Pushgateway (good for histograms/counters across runs)
      - "replace": replace the current group
    """

    key = grouping_key or {}
    if mode == "replace":
        push_to_gateway(pushgateway_url, job=job_name, registry=REGISTRY, grouping_key=key)
    else:
        pushadd_to_gateway(pushgateway_url, job=job_name, registry=REGISTRY, grouping_key=key)
