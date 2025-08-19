import json, threading
from .config import STATE_FILE
from .logging_setup import get_logger
from .config import RIS_FORCE_PROCESS

logger = get_logger(__name__)
_state_lock = threading.Lock()
_STATE: dict[str, list[str]] = {"processed_hashes": []}
def load_state() -> None:
    global _STATE
    if STATE_FILE.exists():
        try:
            _STATE = json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except Exception as e:
            logger.warning(f"State load error: {e}")
def save_state() -> None:
    with _state_lock:
        STATE_FILE.write_text(json.dumps(_STATE, indent=2), encoding='utf-8')
def remember_hash(h: str) -> None:
    with _state_lock:
        lst = _STATE.setdefault('processed_hashes', [])
        if h not in lst:
            lst.append(h); _STATE['processed_hashes'] = lst[-20000:]
    save_state()
def already_processed(h: str) -> bool:
    if RIS_FORCE_PROCESS == "true":
        return False
    with _state_lock:
        return h in _STATE.get('processed_hashes', [])
