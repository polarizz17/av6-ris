# syntax=docker/dockerfile:1.7-labs
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apt-get update && apt-get install -y --no-install-recommends \ 
    build-essential libffi-dev libssl-dev ssh-client     && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app

ENV RIS_WATCH_DIR=/data/incoming RIS_WORK_DIR=/data/work RIS_LOG_DIR=/data/logs RIS_OBSERVER=auto
RUN mkdir -p /data/incoming /data/work /data/logs

RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app /data
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD pgrep -f "python run.py" || exit 1
CMD ["python", "run.py"]
