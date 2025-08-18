from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
from .logging_setup import get_logger
from .utils import is_interesting_file, file_is_stable, sha256_file
from .grouping import GROUPS, derive_group_key
from .state import already_processed
from .config import MAX_WORKERS
logger = get_logger(__name__)
STABILITY_EXEC = ThreadPoolExecutor(max_workers=max(2, MAX_WORKERS // 2))
class DicomHandler(FileSystemEventHandler):
    def on_any_event(self, event) -> None:
        if isinstance(event, (FileCreatedEvent, FileModifiedEvent)):
            p = Path(event.src_path)
            if not is_interesting_file(p): return
            def promote_when_stable(path: Path) -> None:
                try:
                    if not file_is_stable(path): logger.debug(f'Not stable yet: {path.name}'); return
                    h = sha256_file(path)
                    if already_processed(h): logger.info(f'Skip already-processed: {path.name}'); return
                    key = derive_group_key(path); GROUPS.add_file(key, path)
                    logger.info(f'Added to group {key}: {path.name}')
                except Exception as e: logger.warning(f'promote_when_stable error for {path}: {e}')
            STABILITY_EXEC.submit(promote_when_stable, p)
