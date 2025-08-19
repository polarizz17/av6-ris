import os
from pathlib import Path
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

WATCH_DIR = Path(os.getenv("RIS_WATCH_DIR", "./incoming")).resolve()
WORK_DIR = Path(os.getenv("RIS_WORK_DIR", "./work")).resolve()
LOG_DIR = Path(os.getenv("RIS_LOG_DIR", "./logs")).resolve()

STAGING_DIR = WORK_DIR / "staging"
OUTBOX_DIR = WORK_DIR / "outbox"
PROCESSED_DIR = WORK_DIR / "processed"
FAILED_DIR = WORK_DIR / "failed"
for d in (WATCH_DIR, WORK_DIR, LOG_DIR, STAGING_DIR, OUTBOX_DIR, PROCESSED_DIR, FAILED_DIR):
    d.mkdir(parents=True, exist_ok=True)

UPLOAD_METHOD = os.getenv("RIS_UPLOAD_METHOD", "HTTP").upper()
UPLOAD_URL = os.getenv("RIS_UPLOAD_URL", "http://127.0.0.1:8080/upload")
API_TOKEN = os.getenv("API_TOKEN", "")

SFTP_HOST = os.getenv("RIS_SFTP_HOST", "")
SFTP_PORT = int(os.getenv("RIS_SFTP_PORT", "22"))
SFTP_USER = os.getenv("RIS_SFTP_USER", "")
SFTP_PASS = os.getenv("RIS_SFTP_PASS", "")
SFTP_KEY_PATH = os.getenv("RIS_SFTP_KEY_PATH", "")
SFTP_REMOTE_DIR = os.getenv("RIS_SFTP_REMOTE_DIR", "/upload")

S3_BUCKET = os.getenv("RIS_S3_BUCKET", "")
S3_KEY_PREFIX = os.getenv("RIS_S3_KEY_PREFIX", "ris/")
S3_REGION = os.getenv("RIS_S3_REGION", "")
S3_ENDPOINT_URL = os.getenv("RIS_S3_ENDPOINT_URL", "")

ALLOWED_EXTS = {".dcm", ".dicom", ".DCM", ".DICOM"}
IGNORE_SUFFIXES = {".tmp", ".part", ".crdownload"}
IGNORE_HIDDEN = True

STABILITY_CHECK_INTERVAL_SEC = float(os.getenv("RIS_STABILITY_CHECK_INTERVAL", "1.0"))
STABILITY_CHECKS = int(os.getenv("RIS_STABILITY_CHECKS", "2"))
QUIET_PERIOD_SEC = float(os.getenv("RIS_QUIET_PERIOD", "10.0"))
MAX_GROUP_AGE_SEC = float(os.getenv("RIS_MAX_GROUP_AGE", "600"))

MAX_WORKERS = int(os.getenv("RIS_MAX_WORKERS", "4"))
UPLOAD_RETRIES = int(os.getenv("RIS_UPLOAD_RETRIES", "5"))
RETRY_BACKOFF_SEC = float(os.getenv("RIS_RETRY_BACKOFF", "2.0"))

LOG_LEVEL = os.getenv("RIS_LOG_LEVEL", "INFO").upper()
STATE_FILE = WORK_DIR / "state.json"

OBSERVER_BACKEND = os.getenv("RIS_OBSERVER", "auto").lower()

# DICOM compression setting: 'none' or 'jpeg2000_lossless'
DICOM_COMPRESSION = os.getenv("RIS_DICOM_COMPRESSION", "none").strip().lower()
RIS_FORCE_PROCESS = os.getenv("RIS_FORCE_PROCESS", "false").strip().lower()
