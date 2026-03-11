#!/bin/bash

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Terminate all connections and drop and recreate the database
COMMAND=docker
if command_exists podman; then
    COMMAND=podman
fi

$COMMAND compose -f ../docker-compose.e2e.yaml exec database psql -U user -d postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'db' AND pid <> pg_backend_pid();"
$COMMAND compose -f ../docker-compose.e2e.yaml exec database psql -U user -d postgres -c "DROP DATABASE db;"
$COMMAND compose -f ../docker-compose.e2e.yaml exec database psql -U user -d postgres -c "CREATE DATABASE db;"

# Run database migrations
$COMMAND compose -f ../docker-compose.e2e.yaml exec -e LOAD_INITIAL_DATA=True app alembic upgrade head

$COMMAND compose -f ../docker-compose.e2e.yaml exec app python seed_roles_for_cdsp.py

# Run Playwright tests
npx playwright test
