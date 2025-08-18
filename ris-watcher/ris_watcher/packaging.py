import zipfile, hashlib, shutil
from pathlib import Path
from datetime import datetime
from .config import STAGING_DIR, OUTBOX_DIR, WATCH_DIR
from .utils import safe_rel_path
from .compression import compress_if_enabled
from .logging_setup import get_logger
logger = get_logger(__name__)
def build_zip_for_group(group_key: str, files: set[Path]) -> Path:
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    base_name = hashlib.sha1(group_key.encode('utf-8')).hexdigest()[:12]
    zip_name = f'study_{base_name}_{ts}.zip'
    tmp_zip = STAGING_DIR / (zip_name + '.tmp')
    final_zip = OUTBOX_DIR / zip_name
    comp_tmp = STAGING_DIR / (zip_name + '_tmp')
    logger.info(f'Packaging group {group_key} ({len(files)} files) -> {final_zip.name}')
    with zipfile.ZipFile(tmp_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(files):
            if not f.exists():
                logger.warning(f'Skip missing: {f}'); continue
            try:
                rel = safe_rel_path(WATCH_DIR, f)
            except Exception:
                logger.warning(f'Skip outside watch dir: {f}'); continue
            to_write = compress_if_enabled(f, comp_tmp)
            zf.write(to_write, arcname=str(rel))
    tmp_zip.replace(final_zip)
    try:
        if comp_tmp.exists(): shutil.rmtree(comp_tmp, ignore_errors=True)
    except Exception as e:
        logger.warning(f'Cleanup error: {e}')
    return final_zip
