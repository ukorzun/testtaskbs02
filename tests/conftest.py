from __future__ import annotations

import os
import pytest

from framework.config import load_config
from framework.http_client import HttpClient
from framework.logging import setup_logging
from framework.metrics import push_metrics, set_current_test_name
from framework.api.httpbin_api import HttpBinApi

try:
    import pika
except Exception:
    pika = None


@pytest.fixture(scope="session")
def cfg():
    return load_config()


@pytest.fixture(scope="session", autouse=True)
def _logging():
    setup_logging()
    return None


@pytest.fixture(scope="session", autouse=True)
def test_seed():
    """Reproducibility seed for random/Faker.

    - If TEST_SEED is not set, a random seed is generated and attached to Allure.
    - Set TEST_SEED to reproduce the same randomized data.
    """
    seed_raw = os.getenv("TEST_SEED")
    seed = int(seed_raw) if seed_raw else random.randint(1, 2_000_000_000)
    random.seed(seed)

    try:
        from framework import data_gen
        data_gen.fake.seed_instance(seed)
    except Exception:
        pass

    if allure is not None:
        allure.attach(str(seed), name="test.seed", attachment_type=allure.attachment_type.TEXT)

    return seed


@pytest.fixture(scope="session")
def client(cfg) -> HttpClient:
    return HttpClient(service=cfg.service, retry_cfg=cfg.retry)


@pytest.fixture(scope="session")
def api(client) -> HttpBinApi:
    return HttpBinApi(client=client)


@pytest.fixture(autouse=True)
def _current_test(request):
    # Use nodeid for uniqueness across parametrization.
    set_current_test_name(request.node.nodeid)
    yield


def pytest_sessionfinish(session, exitstatus):
    try:
        cfg = load_config()
        if cfg.metrics.enabled:
            grouping_key = {
                "instance": os.getenv("HOSTNAME", "local"),
                "repo": os.getenv("GITHUB_REPOSITORY", "local"),
            }
            push_metrics(cfg.metrics.pushgateway_url, cfg.metrics.job_name, grouping_key=grouping_key, mode="add")
    except Exception:
        return


def pytest_configure(config):
    cfg = load_config()
    pathlib.Path(cfg.reporting.allure_results_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.dirname(cfg.reporting.html_report_path)).mkdir(parents=True, exist_ok=True)
