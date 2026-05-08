#!/usr/bin/env bash
set -euo pipefail
until alembic upgrade head; do
  echo "Waiting for database migrations..."
  sleep 2
done
exec "$@"
