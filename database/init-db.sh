#!/usr/bin/env bash
set -e

export DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@/${POSTGRES_DB}?host=/var/run/postgresql"
export CSV_PATH="/docker-entrypoint-initdb.d/netflix_titles.csv"

echo "Starting Netflix CSV import..."
python /docker-entrypoint-initdb.d/import_netflix.py
echo "Import finished."