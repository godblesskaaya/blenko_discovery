#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/blenko_db_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

docker-compose exec -T postgres pg_dump -U "${POSTGRES_USER:-blenko_admin}" "${POSTGRES_DB:-blenko_discovery}" | gzip > "$BACKUP_FILE"

# Keep last 7 days
find "$BACKUP_DIR" -name "blenko_db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}"
