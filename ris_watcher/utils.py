import time
import hashlib
from pathlib import Path
from datetime import datetime
from .config import (
    WATCH_DIR, ALLOWED_EXTS, IGNORE_SUFFIXES, IGNORE_HIDDEN,
    STABILITY_CHECKS, STABILITY_CHECK_INTERVAL_SEC
)

def now() -> datetime:
    return datetime.utcnow()

def is_hidden(p: Path) -> bool:
    return p.name.startswith(".")

def is_interesting_file(p: Path) -> bool:
    if IGNORE_HIDDEN and is_hidden(p):
        return False
    if p.suffix in IGNORE_SUFFIXES:
        return False
    if p.suffix not in ALLOWED_EXTS:
        return False
    return p.is_file()

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def file_is_stable(p: Path) -> bool:
    try:
        prev = p.stat()
        for _ in range(STABILITY_CHECKS - 1):
            time.sleep(STABILITY_CHECK_INTERVAL_SEC)
            curr = p.stat()
            if curr.st_size != prev.st_size or curr.st_mtime != prev.st_mtime:
                return False
            prev = curr
        return True
    except FileNotFoundError:
        return False

def safe_rel_path(base: Path, target: Path) -> Path:
    return target.resolve().relative_to(base.resolve())
