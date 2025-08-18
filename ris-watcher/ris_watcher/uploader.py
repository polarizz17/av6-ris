import time
from pathlib import Path
from .config import (UPLOAD_METHOD, UPLOAD_URL, API_TOKEN, UPLOAD_RETRIES, RETRY_BACKOFF_SEC, SFTP_HOST, SFTP_PORT, SFTP_USER, SFTP_PASS, SFTP_KEY_PATH, SFTP_REMOTE_DIR, S3_BUCKET, S3_KEY_PREFIX, S3_REGION, S3_ENDPOINT_URL)
from .logging_setup import get_logger
logger = get_logger(__name__)
def _http_upload(zip_path: Path) -> None:
    import requests
    headers: dict[str, str] = {}
    if API_TOKEN: headers['Authorization'] = f'Bearer {API_TOKEN}'
    for attempt in range(1, UPLOAD_RETRIES + 1):
        try:
            with zip_path.open('rb') as f:
                files = {'file': (zip_path.name, f)}
                r = requests.post(UPLOAD_URL, headers=headers, files=files, timeout=60)
            if 200 <= r.status_code < 300: logger.info(f'HTTP uploaded {zip_path.name} ({r.status_code})'); return
            logger.warning(f'HTTP failed {zip_path.name}: {r.status_code} {r.text[:300]}')
        except Exception as e:
            logger.warning(f'HTTP error {zip_path.name} (attempt {attempt}): {e}')
        time.sleep(RETRY_BACKOFF_SEC * attempt)
    raise RuntimeError(f'HTTP upload failed after {UPLOAD_RETRIES} retries')
def _sftp_upload(zip_path: Path) -> None:
    try: import paramiko  # type: ignore
    except Exception as e: raise RuntimeError('paramiko not installed: pip install paramiko') from e
    key = paramiko.RSAKey.from_private_key_file(SFTP_KEY_PATH) if SFTP_KEY_PATH else None
    for attempt in range(1, UPLOAD_RETRIES + 1):
        try:
            transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
            if key: transport.connect(username=SFTP_USER, pkey=key)
            else: transport.connect(username=SFTP_USER, password=SFTP_PASS)
            sftp = paramiko.SFTPClient.from_transport(transport)
            try: sftp.chdir(SFTP_REMOTE_DIR)
            except IOError:
                parts = SFTP_REMOTE_DIR.strip('/').split('/'); cwd = ''
                for p in parts:
                    cwd += '/' + p
                    try: sftp.mkdir(cwd)
                    except IOError: pass
                sftp.chdir(SFTP_REMOTE_DIR)
            remote_path = f"{SFTP_REMOTE_DIR.rstrip('/')}/{zip_path.name}"
            sftp.put(str(zip_path), remote_path)
            sftp.close(); transport.close()
            logger.info(f'SFTP uploaded {zip_path.name} -> {remote_path}'); return
        except Exception as e:
            logger.warning(f'SFTP error (attempt {attempt}): {e}')
            time.sleep(RETRY_BACKOFF_SEC * attempt)
    raise RuntimeError(f'SFTP upload failed after {UPLOAD_RETRIES} retries')
def _s3_upload(zip_path: Path) -> None:
    try: import boto3  # type: ignore
    except Exception as e: raise RuntimeError('boto3 not installed: pip install boto3') from e
    s3 = boto3.client('s3', region_name=S3_REGION or None, endpoint_url=S3_ENDPOINT_URL or None)
    key = f"{S3_KEY_PREFIX.rstrip('/')}/{zip_path.name}"
    for attempt in range(1, UPLOAD_RETRIES + 1):
        try: s3.upload_file(str(zip_path), S3_BUCKET, key); logger.info(f'S3 uploaded {zip_path.name} -> s3://{S3_BUCKET}/{key}'); return
        except Exception as e: logger.warning(f'S3 error (attempt {attempt}): {e}'); time.sleep(RETRY_BACKOFF_SEC * attempt)
    raise RuntimeError(f'S3 upload failed after {UPLOAD_RETRIES} retries')
def upload(zip_path: Path) -> None:
    method = UPLOAD_METHOD.upper()
    if method == 'HTTP': return _http_upload(zip_path)
    if method == 'SFTP': return _sftp_upload(zip_path)
    if method == 'S3': return _s3_upload(zip_path)
    raise ValueError(f'Unknown UPLOAD_METHOD: {UPLOAD_METHOD}')
