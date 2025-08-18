import signal, time
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from .logging_setup import get_logger
from .config import WATCH_DIR, OBSERVER_BACKEND
from .utils import is_interesting_file, file_is_stable, sha256_file
from .grouping import GROUPS, derive_group_key
from .state import load_state
from .watcher import DicomHandler
from .scheduler import start_scheduler, stop_scheduler
logger = get_logger(__name__)
def catchup_scan() -> None:
    logger.info('Catch-up scan starting...')
    for p in WATCH_DIR.rglob('*'):
        if not is_interesting_file(p): continue
        try:
            if not file_is_stable(p): continue
            _ = sha256_file(p)
            key = derive_group_key(p); GROUPS.add_file(key, p)
        except Exception as e: logger.warning(f'Catch-up skip {p}: {e}')
    logger.info('Catch-up scan done.')
def main() -> None:
    logger.info('RIS Watcher starting...'); logger.info(f'Watch dir: {WATCH_DIR}')
    load_state(); catchup_scan()
    _ = start_scheduler()
    handler = DicomHandler()
    observer = PollingObserver() if OBSERVER_BACKEND == 'polling' else Observer()
    observer.schedule(handler, str(WATCH_DIR), recursive=True); observer.start()
    stop_flag: dict[str, bool] = {'stop': False}
    def shutdown(signum=None, frame=None) -> None:
        logger.info(f'Shutdown signal received: {signum}'); stop_flag['stop'] = True; observer.stop()
    signal.signal(signal.SIGINT, shutdown); signal.signal(signal.SIGTERM, shutdown)
    try:
        while not stop_flag['stop']: time.sleep(1.0)
    finally:
        observer.join(timeout=5.0); stop_scheduler(); logger.info('RIS Watcher stopped cleanly.')
