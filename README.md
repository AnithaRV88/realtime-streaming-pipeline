# Real-time streaming pipeline

Kafka → Spark Structured Streaming → Delta Lake / PostgreSQL → Grafana (work in progress).

**Project root:** all pipeline code and infra for this effort live under this directory (not under `.cursor/projects`).

## Infrastructure (local)

1. Start ZooKeeper, Kafka, and PostgreSQL:

   ```powershell
   docker compose up -d
   ```

2. Create Kafka topics (`user-events` with 3 partitions, `user-events-dlq`):

   ```powershell
   .\scripts\create-topics.ps1
   ```

   On Linux or macOS:

   ```bash
   chmod +x scripts/create-topics.sh
   ./scripts/create-topics.sh
   ```

- **Kafka (host):** `localhost:9092` — use as `bootstrap.servers` for producers and Spark on your machine.
- **PostgreSQL:** `localhost:5432`; defaults: user/password/database `streaming` (override via `.env`; see `.env.example`).

### If `docker compose up` fails with `bitnami/zookeeper` / `bitnami/kafka` “not found”

Public **`docker.io/bitnami/*`** tags for these stacks often no longer resolve on Docker Hub. This repo uses **`docker.io/bitnamilegacy/*`** pin tags instead.

From `C:\MyProjects\realtime-streaming-pipeline`, confirm what Compose will pull:

```powershell
Select-String -Path .\docker-compose.yml -Pattern "image:"
```

You should see `bitnamilegacy/zookeeper` and `bitnamilegacy/kafka`. If you still see `bitnami/zookeeper`, refresh the file from git or replace those `image:` lines with the versions in the current [`docker-compose.yml`](docker-compose.yml), then:

```powershell
docker compose pull
docker compose up -d
```

Postgres showing “Interrupted” is normal when another service’s image pull fails first.

## Python producer

From the project root, create a venv, install dependencies, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m producer --bootstrap-servers localhost:9092 --topic user-events --mode synthetic --interval 0.5
```

Optional live Wikimedia feed (same JSON schema; still one publish every `--interval` seconds):

```powershell
python -m producer --mode wikimedia --interval 0.5
```

Messages are UTF-8 JSON with fields `event_id`, `event_time`, `event_type`, `user_id`, `source`, `payload` (object), and `status` (`ok` | `error`). Synthetic mode randomly marks a small fraction as `error` (see `--error-rate`) for error-rate dashboards later.
