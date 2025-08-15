FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libffi-dev libssl-dev ssh-client && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app
ENV RIS_WATCH_DIR=/data/incoming RIS_WORK_DIR=/data/work RIS_LOG_DIR=/data/logs RIS_OBSERVER=auto
RUN mkdir -p /data/incoming /data/work /data/logs
USER root
CMD ["python", "run.py"]
