from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml
from dotenv import load_dotenv


def _as_bool(v: str | None, default: bool = False) -> bool:
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class ServiceConfig:
    base_url: str
    timeout_s: float


@dataclass(frozen=True)
class RetryConfig:
    attempts: int
    backoff_s: float
    backoff_multiplier: float
    retry_on_statuses: List[int]


@dataclass(frozen=True)
class ReportingConfig:
    allure_results_dir: str
    html_report_path: str


@dataclass(frozen=True)
class MetricsConfig:
    enabled: bool
    pushgateway_url: str
    job_name: str


@dataclass(frozen=True)
class AppConfig:
    service: ServiceConfig
    retry: RetryConfig
    reporting: ReportingConfig
    metrics: MetricsConfig


def load_config(config_path: str = "config/config.yaml", env_path: Optional[str] = ".env") -> AppConfig:
    # Environment overrides are handy for CI/CD or docker.
    if env_path and Path(env_path).exists():
        load_dotenv(env_path)

    raw = {}
    p = Path(config_path)
    if p.exists():
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    # YAML defaults
    service = raw.get("service", {})
    retry = raw.get("retry", {})
    reporting = raw.get("reporting", {})
    metrics = raw.get("metrics", {})

    # ENV overrides
    base_url = os.getenv("BASE_URL", service.get("base_url", "https://httpbin.org"))
    timeout_s = float(os.getenv("TIMEOUT_S", service.get("timeout_s", 10)))

    attempts = int(os.getenv("RETRY_ATTEMPTS", retry.get("attempts", 3)))
    backoff_s = float(os.getenv("RETRY_BACKOFF_S", retry.get("backoff_s", 0.4)))
    backoff_multiplier = float(os.getenv("RETRY_BACKOFF_MULTIPLIER", retry.get("backoff_multiplier", 2.0)))

    statuses_env = os.getenv("RETRY_ON_STATUSES")
    if statuses_env:
        retry_on_statuses = [int(x.strip()) for x in statuses_env.split(",") if x.strip()]
    else:
        retry_on_statuses = [int(x) for x in retry.get("retry_on_statuses", [429, 500, 502, 503, 504])]

    allure_results_dir = os.getenv("ALLURE_RESULTS_DIR", reporting.get("allure_results_dir", "artifacts/allure-results"))
    html_report_path = os.getenv("HTML_REPORT_PATH", reporting.get("html_report_path", "artifacts/report.html"))

    metrics_enabled = _as_bool(os.getenv("METRICS_ENABLED"), bool(metrics.get("enabled", True)))
    pushgateway_url = os.getenv("PUSHGATEWAY_URL", metrics.get("pushgateway_url", "http://pushgateway:9091"))
    job_name = os.getenv("METRICS_JOB_NAME", metrics.get("job_name", "httpbin_tests"))

    return AppConfig(
        service=ServiceConfig(base_url=base_url, timeout_s=timeout_s),
        retry=RetryConfig(
            attempts=attempts,
            backoff_s=backoff_s,
            backoff_multiplier=backoff_multiplier,
            retry_on_statuses=retry_on_statuses,
        ),
        reporting=ReportingConfig(allure_results_dir=allure_results_dir, html_report_path=html_report_path),
        metrics=MetricsConfig(enabled=metrics_enabled, pushgateway_url=pushgateway_url, job_name=job_name),
    )
