FROM postgres:16

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
 && rm -rf /var/lib/apt/lists/* \
 && python3 -m venv /opt/venv

COPY database/requirements.txt /tmp/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

COPY database/schema.sql /docker-entrypoint-initdb.d/01-schema.sql
COPY database/import_netflix.py /docker-entrypoint-initdb.d/import_netflix.py
COPY data/netflix_titles.csv /docker-entrypoint-initdb.d/netflix_titles.csv
COPY database/init-db.sh /docker-entrypoint-initdb.d/02-init-db.sh

RUN chmod +x /docker-entrypoint-initdb.d/02-init-db.sh

EXPOSE 5432