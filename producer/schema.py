"""Canonical JSON event shape shared with Spark Structured Streaming."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Mapping

REQUIRED_FIELDS = frozenset(
    {"event_id", "event_time", "event_type", "user_id", "source", "payload", "status"}
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def validate_event(event: Mapping[str, Any]) -> None:
    missing = REQUIRED_FIELDS - event.keys()
    if missing:
        raise ValueError(f"event missing fields: {sorted(missing)}")
    if not isinstance(event["payload"], dict):
        raise ValueError("payload must be an object")
    if event["status"] not in ("ok", "error"):
        raise ValueError('status must be "ok" or "error"')


def event_to_json_bytes(event: Mapping[str, Any]) -> bytes:
    validate_event(event)
    return json.dumps(event, separators=(",", ":"), sort_keys=False, default=str).encode(
        "utf-8"
    )
