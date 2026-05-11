"""Map Wikimedia recentchange SSE events into the canonical pipeline schema."""

from __future__ import annotations

import json
import uuid
from typing import Any, Iterator

import requests

from producer.schema import utc_now_iso

WIKIMEDIA_RECENTCHANGE_URL = "https://stream.wikimedia.org/v2/stream/recentchange"


def _map_recentchange(data: dict[str, Any]) -> dict[str, Any]:
    """Turn one Wikimedia recentchange JSON object into a canonical event."""
    rc_type = data.get("type") or "unknown"
    title = data.get("title") or ""
    wiki = data.get("wiki") or ""
    user = data.get("user") or "anonymous"
    comment = (data.get("comment") or "")[:500]

    return {
        "event_id": str(uuid.uuid4()),
        "event_time": utc_now_iso(),
        "event_type": "wiki_edit",
        "user_id": user,
        "source": "wikimedia",
        "payload": {
            "rc_type": rc_type,
            "title": title,
            "wiki": wiki,
            "comment": comment,
            "namespace": data.get("namespace"),
            "meta_uri": (data.get("meta") or {}).get("uri"),
        },
        "status": "ok",
    }


def iter_wikimedia_events(url: str = WIKIMEDIA_RECENTCHANGE_URL) -> Iterator[dict[str, Any]]:
    """
    Yield canonical events from the public Wikimedia EventStream (SSE).

    Long-lived HTTP connection; stop with Ctrl+C / closing the process.
    """
    headers = {"Accept": "text/event-stream", "User-Agent": "realtime-streaming-pipeline/1.0"}
    with requests.get(url, stream=True, headers=headers, timeout=(10, None)) as resp:
        resp.raise_for_status()
        for raw in resp.iter_lines(decode_unicode=True):
            if raw is None:
                continue
            line = raw.strip()
            if not line or line.startswith(":"):
                continue
            if line.startswith("data:"):
                payload = line[5:].strip()
                if not payload:
                    continue
                try:
                    obj = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                yield _map_recentchange(obj)
