import threading, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from .config import MAX_WORKERS, QUIET_PERIOD_SEC, PROCESSED_DIR, FAILED_DIR
from .logging_setup import get_logger
from .grouping import GROUPS
from .packaging import build_zip_for_group
from .uploader import upload
from .state import remember_hash
from .utils import sha256_file
logger = get_logger(__name__)
stop_event = threading.Event()
EXEC = ThreadPoolExecutor(max_workers=MAX_WORKERS)
def _move(src: Path, dst_dir: Path) -> Path | None:
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        target = dst_dir / src.name
        src.replace(target); return target
    except Exception as e:
        logger.error(f'Failed to move {src} -> {dst_dir}: {e}'); return None
def _process_group(group) -> None:
    zip_path: Path | None = None
    try:
        zip_path = build_zip_for_group(group.key, group.files)
        upload(zip_path)
        for f in group.files:
            try: remember_hash(sha256_file(f))
            except Exception as e: logger.warning(f'Hash remember failed for {f}: {e}')
        _move(zip_path, PROCESSED_DIR)
        logger.info(f'Group processed: {group.key}')
    except Exception as e:
        logger.exception(f'Group processing failed: {group.key} -> {e}')
        if zip_path and zip_path.exists(): _move(zip_path, FAILED_DIR)
def scheduler_loop() -> None:
    logger.info('Scheduler loop started')
    while not stop_event.is_set():
        try:
            ready = GROUPS.harvest_ready(QUIET_PERIOD_SEC)
            for g in ready: EXEC.submit(_process_group, g)
        except Exception as e: logger.exception(f'Scheduler error: {e}')
        time.sleep(1.0)
    logger.info('Scheduler loop exiting')
def start_scheduler() -> threading.Thread:
    t = threading.Thread(target=scheduler_loop, name='Scheduler', daemon=True); t.start(); return t
def stop_scheduler() -> None:
    stop_event.set(); EXEC.shutdown(wait=True)
