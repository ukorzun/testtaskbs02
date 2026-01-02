# testtaskbs01

This repo implements a **senior-grade API automation framework** in Python (**pytest**) against `httpbin`.

Covers (base scope):
- Response formats
- Request inspection
- Dynamic data
- Config support via **YAML + optional .env overrides**
- **Custom retry decorator** with attempt-by-attempt logging
- Randomized test data via **Faker**
- Reporting via **Allure** and **HTML** (pytest-html), generated automatically in CI

Bonus tracks included:
- RabbitMQ messaging test (publish + consume)
- Dockerized environment (`docker-compose`) with healthchecks (no sleeps)
- Observability: Prometheus + Pushgateway + Grafana dashboard (retries + p95 duration)

---

## Project structure

- `framework/` – reusable test framework (config, http client, retry, data gen, metrics)
- `tests/` – pytest tests grouped by assignment topics
- `config/config.yaml` – defaults
- `.env.example` – optional overrides
- `docker/` – bonus docker-compose + monitoring stack
- `artifacts/` – test reports output folder (created automatically)

---

## Local setup

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
```

Optional (bonus messaging test):
```bash
pip install -r requirements-messaging.txt
```

### 2) Run tests

Allure results:
```bash
pytest --alluredir=artifacts/allure-results
```

HTML report:
```bash
pytest --html=artifacts/report.html --self-contained-html
```

Both:
```bash
pytest --alluredir=artifacts/allure-results --html=artifacts/report.html --self-contained-html
```

### 3) View reports

**HTML:** open `artifacts/report.html`.

**Allure:**
```bash
# requires allure CLI installed on your machine
allure serve artifacts/allure-results
```

---

## Config

Defaults live in `config/config.yaml`. Any value can be overridden via `.env`:

- `BASE_URL`, `TIMEOUT_S`
- `RETRY_ATTEMPTS`, `RETRY_BACKOFF_S`, `RETRY_BACKOFF_MULTIPLIER`, `RETRY_ON_STATUSES`
- `ALLURE_RESULTS_DIR`, `HTML_REPORT_PATH`
- `METRICS_ENABLED`, `PUSHGATEWAY_URL`, `METRICS_JOB_NAME`

---

## Docker (bonus)

From repo root:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

What you get:
- httpbin on http://localhost:8080
- RabbitMQ UI on http://localhost:15672 (admin: guest / guest)
- Prometheus on http://localhost:9090
- Grafana on http://localhost:3000 (admin/admin)
- Tests container runs pytest and writes reports into a **Docker named volume** (`artifacts`) to avoid Docker Desktop file-sharing issues on macOS.

To copy reports to the host:

```bash
docker cp docker-tests-1:/app/artifacts ./artifacts
```

Grafana includes a provisioned dashboard:
- Folder: **QA**
- Dashboard: **QA Tests - Metrics**
  - Test duration p95 (Prometheus histogram_quantile)
  - Retry attempts rate

---

## Notes (senior-level design choices)

- **Retry**:
  - retries on network issues + configurable status codes
  - logs timing and delay for each attempt
- **Models**:
  - httpbin responses validated with Pydantic for strong schema checks
- **Metrics**:
  - Tests emit Prometheus metrics and push them at session end (never fails build if unavailable)


## Test Strategy (QA Automation)

Цель репозитория — показать **QA Automation подход**, а не “dev-tests”:

- **Поведенческие проверки**: корректная обработка ошибок/таймаутов/ретраев (см. `tests/test_resilience_*`).
- **Контракты**: строгие модели Pydantic (`extra='forbid'`, `UUID4`) — раннее обнаружение breaking changes.
- **Границы и данные**: спецсимволы/Unicode/размер payload (см. `tests/test_data_boundaries.py`).
- **Воспроизводимость**: `TEST_SEED` фиксирует генерацию данных; seed прикладывается в Allure.
- **Управляемость прогона**: маркеры `smoke/regression/resilience/data/integration`.

### Quick run

```bash
pip install -r requirements.txt
TEST_SEED=123 pytest --alluredir=artifacts/allure-results --html=artifacts/report.html --self-contained-html
```


## Integration tests (RabbitMQ)

Integration test: `tests/integration/test_messaging_rabbitmq.py`

Install dependency:
```bash
pip install -r requirements-messaging.txt
```

Run RabbitMQ (option 1 — docker compose from repo):
```bash
docker compose -f docker/docker-compose.yml up -d rabbitmq
```

Run integration tests:
```bash
export AMQP_URL="amqp://guest:guest@localhost:5672/%2F"
pytest -m integration
```

Note: default vhost is `/` and must be URL-encoded as `%2F` in AMQP_URL.
If RabbitMQ isn't reachable, the integration test will be **skipped** with a clear message (not failed).
