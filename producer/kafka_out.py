"""Confluent Kafka producer with delivery callbacks and clean shutdown."""

from __future__ import annotations

import logging
import signal
import sys
import time
from typing import Any, Callable

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


def build_producer(bootstrap_servers: str) -> Producer:
    return Producer(
        {
            "bootstrap.servers": bootstrap_servers,
            "acks": "all",
            "enable.idempotence": True,
            "linger.ms": 5,
            "batch.size": 65536,
        }
    )


def delivery_report(err: Any, msg: Any) -> None:
    if err is not None:
        logger.error("delivery failed: %s", err)
    else:
        logger.debug("delivered to %s [%d] @ %d", msg.topic(), msg.partition(), msg.offset())


def produce_loop(
    *,
    bootstrap_servers: str,
    topic: str,
    next_payload: Callable[[], bytes],
    interval_sec: float,
    stop_flag: list[bool],
) -> None:
    prod = build_producer(bootstrap_servers)

    def handle_sigint(_sig: int, _frame: Any) -> None:
        stop_flag[0] = True

    signal.signal(signal.SIGINT, handle_sigint)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, handle_sigint)

    while not stop_flag[0]:
        payload = next_payload()
        prod.produce(topic, payload, on_delivery=delivery_report)
        prod.poll(0)
        time.sleep(interval_sec)

    prod.flush(30)
