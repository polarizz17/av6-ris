from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from typing import Tuple
from .logging_setup import get_logger
from .config import DICOM_COMPRESSION
logger = get_logger(__name__)
GDCM_TARGETS = {
    "jpeg2000_lossless": ["--j2k", "--lossless"],
}
def _has_gdcmconv() -> bool:
    return shutil.which("gdcmconv") is not None
def _gdcm_compress(src: Path, dst: Path, mode: str) -> Tuple[bool, str]:
    args = GDCM_TARGETS.get(mode)
    if not args:
        return False, f"Unsupported compression mode: {mode}"
    cmd = ["gdcmconv", *args, str(src), str(dst)]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if res.returncode == 0 and dst.exists() and dst.stat().st_size > 0:
            return True, "ok"
        return False, f"gdcmconv failed ({res.returncode}): {res.stderr.strip()[:300]}"
    except Exception as e:
        return False, f"gdcmconv error: {e}"
def compress_if_enabled(src: Path, tmp_dir: Path) -> Path:
    mode = (DICOM_COMPRESSION or 'none').lower()
    if mode in ('', 'none'):
        return src
    if not _has_gdcmconv():
        logger.warning('Compression requested but gdcmconv not found; using original file.')
        return src
    tmp_dir.mkdir(parents=True, exist_ok=True)
    dst = tmp_dir / (src.stem + '.dcm')
    ok, msg = _gdcm_compress(src, dst, mode)
    if ok:
        logger.info(f'Compressed {src.name} -> {dst.name} ({mode})')
        return dst
    logger.warning(f'Compression skipped for {src.name}: {msg}')
    return src
