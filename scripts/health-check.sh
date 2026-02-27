#!/usr/bin/env bash
set -euo pipefail

# Ensure all expected services are running
running_services="$(docker-compose ps --services --status running | wc -l | tr -d ' ')"
if [ "$running_services" -lt 3 ]; then
  echo "ERROR: expected 3 running services, got ${running_services}"
  docker-compose ps
  exit 1
fi

# Backend health
backend_status="$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || true)"
if [ "$backend_status" != "200" ]; then
  echo "ERROR: backend health check failed (${backend_status})"
  exit 1
fi

# Frontend health
frontend_status="$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health || true)"
if [ "$frontend_status" != "200" ]; then
  echo "ERROR: frontend health check failed (${frontend_status})"
  exit 1
fi

# Postgres readiness
docker-compose exec -T postgres pg_isready -U "${POSTGRES_USER:-blenko_admin}" -d "${POSTGRES_DB:-blenko_discovery}" >/dev/null

echo "All services healthy"
