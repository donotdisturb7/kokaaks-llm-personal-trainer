#!/usr/bin/env bash
set -euo pipefail

# Simple helper to kill common ports, reset docker compose stack, and relaunch

PROJECT_NAME="kokaaks-llm-personal-trainer"
PORTS=(3001 8002 9001 5435 6381)

echo "[1/5] Killing processes on ports: ${PORTS[*]}"
for p in "${PORTS[@]}"; do
  if command -v fuser >/dev/null 2>&1; then
    fuser -k -n tcp "$p" 2>/dev/null || true
  fi
  if command -v lsof >/dev/null 2>&1; then
    pid=$(lsof -ti tcp:"$p" || true)
    if [[ -n "${pid}" ]]; then
      kill -9 ${pid} || true
    fi
  fi
done

echo "[2/5] Bringing docker compose down (volumes + orphans)"
docker compose down -v --remove-orphans || true

echo "[3/5] Stopping any running Docker containers bound to target ports"
# Find any containers publishing the listed ports and stop/remove them
for p in "${PORTS[@]}"; do
  # Parse docker ps Ports column and find containers exposing host port p
  mapfile -t matches < <(docker ps --format '{{.ID}} {{.Ports}}' | grep -E "(^| )[a-f0-9]+ .*:${p}->" || true)
  for line in "${matches[@]}"; do
    cid=$(echo "$line" | awk '{print $1}')
    if [[ -n "${cid}" ]]; then
      echo " - Stopping container $cid using port $p"
      docker stop "$cid" >/dev/null 2>&1 || true
      docker rm "$cid" >/dev/null 2>&1 || true
    fi
  done
done

echo "[4/5] Building and starting containers"
docker compose up -d --build

echo "[5/5] Waiting for healthchecks (postgres, backend, proxy)"
wait_for_healthy() {
  local svc=$1
  local tries=60
  local i=0
  while [[ $i -lt $tries ]]; do
    status=$(docker inspect --format='{{json .State.Health.Status}}' "$svc" 2>/dev/null || echo '"starting"')
    if [[ "$status" == '"healthy"' ]]; then
      echo " - $svc is healthy"
      return 0
    fi
    sleep 2
    i=$((i+1))
  done
  echo " - WARNING: $svc not healthy after timeout"
}

wait_for_healthy kovaaks-postgres || true
wait_for_healthy kovaaks-backend || true
wait_for_healthy kovaaks-proxy || true

echo "[post] Ensuring pgvector extension is enabled"
docker compose exec -T postgres psql -U kovaaks -d kovaaks_ai -c "CREATE EXTENSION IF NOT EXISTS vector;" || echo " - Extension already enabled or error"

echo "[post] Applying database migrations (backend)"
docker compose exec -T -e ALEMBIC_DATABASE_URL=postgresql://kovaaks:kovaaks_pass@postgres:5432/kovaaks_ai backend alembic upgrade head || echo " - Skipped migrations (backend not ready?)"

echo "✅ Done. Services should be available:"
echo " - Frontend:   http://localhost:3001"
echo " - Backend:    http://localhost:8002 (health: /health)"
echo " - Proxy:      http://localhost:9001 (health: /health)"

