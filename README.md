# RIS Watcher (DICOM → ZIP → Upload)

Cross-platform Python service that:
- Watches a folder in real time for DICOM files
- Groups by StudyInstanceUID (if `pydicom` present) or by folder
- Creates ZIP archives
- Uploads via HTTP / SFTP / S3
- Type-checked (mypy), linted (ruff), formatted (black)
- Docker + docker-compose, pre-commit hooks

## Local quick start
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
cp .env.example .env
mkdir -p incoming
python run.py
```

Type/lint:
```bash
mypy . && ruff check . && black --check .
```

## Docker (macOS-friendly)
```bash
mkdir -p host_data/incoming host_data/work host_data/logs
docker compose up -d --build
docker compose logs -f
```
If volume events are flaky on macOS, set `RIS_OBSERVER=polling` in `.env` or `docker-compose.yml`.

## Configure upload
Set `RIS_UPLOAD_METHOD=HTTP|SFTP|S3` and fill the respective envs in `.env`.
