from __future__ import annotations

import json
import os
import time

import pytest
import allure

allure.dynamic.suite("Integration")

try:
    import pika
    from pika.exceptions import AMQPConnectionError
except Exception:  # pragma: no cover
    pika = None
    AMQPConnectionError = Exception


# Only pytest marker here. Allure labels should be set via allure.* decorators, not pytest marks.
pytestmark = pytest.mark.integration


def _connect(amqp_url: str, attempts: int = 5, delay_s: float = 1.0):
    """Connect to RabbitMQ with retries and sane timeouts for CI/docker."""
    if pika is None:
        raise RuntimeError("pika is not installed")

    params = pika.URLParameters(amqp_url)

    # Stability knobs:
    params.connection_attempts = 1  # we implement our own retry loop
    params.retry_delay = 0
    params.socket_timeout = float(os.getenv("AMQP_SOCKET_TIMEOUT_S", "5"))
    params.blocked_connection_timeout = float(os.getenv("AMQP_BLOCKED_TIMEOUT_S", "10"))
    params.heartbeat = int(os.getenv("AMQP_HEARTBEAT_S", "0"))  # 0 disables heartbeats for short tests

    last = None
    for i in range(1, attempts + 1):
        try:
            return pika.BlockingConnection(params)
        except AMQPConnectionError as e:
            last = e
            if i == attempts:
                raise
            time.sleep(delay_s)
    raise last  # pragma: no cover


@allure.story("Messaging integration")
@allure.feature("Messaging")
@allure.label("layer", "integration")
@allure.title("Bonus: RabbitMQ publish/consume roundtrip")
def test_publish_and_consume_rabbitmq():
    """Publishes a message and consumes it within the test.

    Run:
      pip install -r requirements-messaging.txt
      docker compose -f docker/docker-compose.yml up -d rabbitmq
      export AMQP_URL="amqp://guest:guest@localhost:5672/%2F"
      pytest -m integration
    """
    if pika is None:
        pytest.skip("pika is not installed. Install requirements-messaging.txt to run integration tests.")

    amqp_url = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/%2F")
    queue = os.getenv("AMQP_QUEUE", "qa.events")

    try:
        with allure.step(f"Connect to RabbitMQ: {amqp_url}"):
            conn = _connect(amqp_url)
    except Exception as e:
        pytest.skip(f"RabbitMQ not reachable via AMQP_URL={amqp_url!r}. Start RabbitMQ or fix URL. Details: {e}")

    ch = conn.channel()
    with allure.step(f"Declare queue: {queue}"):
        ch.queue_declare(queue=queue, durable=False, auto_delete=True)

    payload = {"event": "ping", "ts": time.time()}
    body = json.dumps(payload).encode("utf-8")

    with allure.step("Publish message"):
        ch.basic_publish(exchange="", routing_key=queue, body=body)

    # Consume with a short polling loop (more robust than a single basic_get)
    deadline = time.time() + 5
    got = None
    with allure.step("Consume message"):
        while time.time() < deadline and got is None:
            method, props, msg = ch.basic_get(queue=queue, auto_ack=True)
            if method:
                got = json.loads(msg.decode("utf-8"))
                break
            time.sleep(0.2)

    conn.close()

    with allure.step("Assert consumed payload"):
        assert got is not None, "Message was not consumed from queue in time"
        assert got["event"] == "ping"
