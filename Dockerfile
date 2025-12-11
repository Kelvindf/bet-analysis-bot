# Python slim base
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1

# System deps for psycopg2-binary might not be needed, but add gcc & libpq if building psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl netcat-openbsd     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Default command waits DB and runs app; can be overridden by docker-compose
CMD ["/bin/bash", "-lc", "python -u scripts/wait_for_db.py && python -u src/main.py"]
