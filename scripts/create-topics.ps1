# Requires: Docker Compose stack running (kafka service healthy).
# Creates user-events (3 partitions) and user-events-dlq for the streaming pipeline.

$ErrorActionPreference = "Stop"
$composeFile = Join-Path (Split-Path $PSScriptRoot -Parent) "docker-compose.yml"

docker compose -f $composeFile exec -T kafka /opt/bitnami/kafka/bin/kafka-topics.sh `
  --bootstrap-server kafka:29092 `
  --create `
  --if-not-exists `
  --topic user-events `
  --partitions 3 `
  --replication-factor 1

docker compose -f $composeFile exec -T kafka /opt/bitnami/kafka/bin/kafka-topics.sh `
  --bootstrap-server kafka:29092 `
  --create `
  --if-not-exists `
  --topic user-events-dlq `
  --partitions 3 `
  --replication-factor 1

Write-Host "Topics ready. Listing:"
docker compose -f $composeFile exec -T kafka /opt/bitnami/kafka/bin/kafka-topics.sh `
  --bootstrap-server kafka:29092 `
  --list
