#!/usr/bin/env bash
# Requires: Docker Compose stack running (kafka service healthy).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="${ROOT}/docker-compose.yml"

docker compose -f "${COMPOSE_FILE}" exec -T kafka /opt/bitnami/kafka/bin/kafka-topics.sh \
  --bootstrap-server kafka:29092 \
  --create \
  --if-not-exists \
  --topic user-events \
  --partitions 3 \
  --replication-factor 1

docker compose -f "${COMPOSE_FILE}" exec -T kafka /opt/bitnami/kafka/bin/kafka-topics.sh \
  --bootstrap-server kafka:29092 \
  --create \
  --if-not-exists \
  --topic user-events-dlq \
  --partitions 3 \
  --replication-factor 1

echo "Topics ready. Listing:"
docker compose -f "${COMPOSE_FILE}" exec -T kafka /opt/bitnami/kafka/bin/kafka-topics.sh \
  --bootstrap-server kafka:29092 \
  --list
