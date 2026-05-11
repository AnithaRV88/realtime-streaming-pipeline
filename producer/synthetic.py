"""Synthetic clickstream / IoT-style events using Faker."""

from __future__ import annotations

import random
import uuid

from faker import Faker

from producer.schema import utc_now_iso

_fake = Faker()
_fake.seed_instance()


EVENT_TYPES = (
    "page_view",
    "button_click",
    "sensor_temperature",
    "sensor_humidity",
    "checkout_started",
)


def build_synthetic_event(error_rate: float = 0.02) -> dict:
    """One JSON-serializable event dict matching :mod:`producer.schema`."""
    event_type = random.choice(EVENT_TYPES)
    is_error = random.random() < error_rate
    status = "error" if is_error else "ok"

    if event_type.startswith("sensor_"):
        payload = {
            "device_id": f"dev-{uuid.uuid4().hex[:8]}",
            "value": round(random.uniform(10.0, 35.0), 2),
            "unit": "c" if "temperature" in event_type else "pct",
        }
    else:
        payload = {
            "path": _fake.uri_path(),
            "referrer": _fake.uri_path() if random.random() > 0.5 else None,
        }

    return {
        "event_id": str(uuid.uuid4()),
        "event_time": utc_now_iso(),
        "event_type": event_type,
        "user_id": str(uuid.uuid4()),
        "source": "synthetic",
        "payload": payload,
        "status": status,
    }
