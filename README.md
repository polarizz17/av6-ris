# RIS System (Watcher + Upload Server) with Lossless DICOM Compression

This bundle runs:
- **ris-upload-server** (FastAPI) at http://localhost:8080 (saves uploads to `ris-upload-server/archive`)
- **ris-watcher** (Python) watches `ris-watcher/incoming`, compresses DICOMs (lossless JPEG 2000), zips, and uploads

## Start
```bash
docker compose up -d --build
docker compose logs -f
```

## Drop DICOM files
Place `.dcm` files in `./ris-watcher/incoming/`

## Compression
The watcher can compress DICOMs (lossless JPEG 2000) before zipping.
Set in `ris-watcher/.env`:
```
RIS_DICOM_COMPRESSION=jpeg2000_lossless   # or 'none'
```
We use `gdcmconv` from **gdcm-tools** inside the watcher Docker image.

## Auth
Both services share `API_TOKEN=changeme` by default (see `.env` files). Change both to the same value if needed.
