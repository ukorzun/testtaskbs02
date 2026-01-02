# QA Automation Test Framework

## Stack
- Python + pytest
- Allure / HTML reports
- RabbitMQ
- Docker Compose
- Prometheus + Grafana

## Target API
https://httpbin.org/

## Covered Scope
- Response formats
- Request inspection
- Dynamic / randomized data
- Messaging integration (RabbitMQ publish → consume)
- Retry logic with detailed logging
- Metrics & observability

## Run environment
```bash
docker compose up -d --build
```

### Services
- HttpBin: http://localhost:8080
- RabbitMQ UI: http://localhost:15672 (guest / guest)
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin)

## Run tests
All tests:
```bash
docker compose run --rm tests pytest
```

Integration tests (RabbitMQ):
```bash
docker compose run --rm tests pytest -m integration -vv
```

## Reports
- Allure results: artifacts/allure-results
- HTML report: artifacts/report.html
- Allure report is published in CI (GitHub Pages)

## Messaging Integration
- Broker: RabbitMQ
- Queue: qa.events
- Test publishes a message and validates its consumption
- Verified locally and in CI

## Observability
Custom metrics pushed to Pushgateway:
- test_duration_seconds
- test_retries_total

### Verification
- Prometheus targets: http://localhost:9090/targets
- Grafana dashboard: QA / Tests Metrics

## Configuration
- YAML / .env based configuration
- Environment variables override defaults

## CI
- Ruff linting
- Pytest execution
- Allure and HTML reports as artifacts

✔ All assignment requirements are implemented and verifiable.
