# RIS System (Watcher + Upload Server)

This bundle runs:
- **ris-upload-server** (FastAPI) at http://localhost:8080 (saves uploads to `ris-upload-server/archive`)
- **ris-watcher** (Python service) that watches `ris-watcher/incoming`, zips DICOMs, uploads to the server

## One-command start
```bash
docker compose up -d --build
docker compose logs -f
```

## Where to drop files
Put DICOM files into `./ris-watcher/incoming/`. The watcher groups them, zips, and POSTs to the server.

## Auth
Both sides use the same token by default: `changeme` (see `ris-watcher/.env` and `ris-upload-server/.env`).

## Tuning
- Edit `ris-watcher/.env` for stability, grouping, and upload settings.
- On macOS, if file events are flaky on bind mounts, set `RIS_OBSERVER=polling` in `ris-watcher/.env`.
