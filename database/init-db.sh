#!/usr/bin/env bash
set -e

export DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"
export CSV_PATH="/docker-entrypoint-initdb.d/netflix_titles.csv"

echo "Starting Netflix CSV import..."
python /docker-entrypoint-initdb.d/import_netflix.py
echo "Import finished."