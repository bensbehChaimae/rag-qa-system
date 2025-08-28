#!/bin/bash
set -e 


echo "Running database migrations..."
cd /app/models/db_schemas/ragdb/
alembic upgrade head
cd /app


echo "Starting FastAPI server..."
exec "$@"

