"""CLI: synthetic (500 ms) or Wikimedia-backed producer into Kafka."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from producer import kafka_out
from producer.schema import event_to_json_bytes, validate_event
from producer.synthetic import build_synthetic_event
from producer.wikimedia import iter_wikimedia_events


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Publish canonical JSON events to Kafka.")
    p.add_argument(
        "--bootstrap-servers",
        default="localhost:9092",
        help="Kafka bootstrap servers (default: localhost:9092)",
    )
    p.add_argument("--topic", default="user-events", help="Target topic (default: user-events)")
    p.add_argument(
        "--mode",
        choices=("synthetic", "wikimedia"),
        default="synthetic",
        help="synthetic: Faker IoT/clickstream every --interval; wikimedia: public recentchange stream",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Seconds between events (default: 0.5). Wikimedia is high-volume; one event per interval is sent.",
    )
    p.add_argument(
        "--error-rate",
        type=float,
        default=0.02,
        help="Synthetic only: fraction of events with status=error (default: 0.02)",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="DEBUG logging")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    stop_flag: list[bool] = [False]

    if args.mode == "synthetic":

        def next_payload() -> bytes:
            ev = build_synthetic_event(error_rate=args.error_rate)
            validate_event(ev)
            return event_to_json_bytes(ev)

        kafka_out.produce_loop(
            bootstrap_servers=args.bootstrap_servers,
            topic=args.topic,
            next_payload=next_payload,
            interval_sec=args.interval,
            stop_flag=stop_flag,
        )
        return 0

    # wikimedia: iterator may block; pull one event per interval
    it = iter_wikimedia_events()

    def next_wiki_payload() -> bytes:
        ev = next(it)
        validate_event(ev)
        return event_to_json_bytes(ev)

    kafka_out.produce_loop(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        next_payload=next_wiki_payload,
        interval_sec=args.interval,
        stop_flag=stop_flag,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
