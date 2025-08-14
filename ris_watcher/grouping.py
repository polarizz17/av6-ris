from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from datetime import timedelta
from typing import Dict, Set, List
from .utils import now
from .config import MAX_GROUP_AGE_SEC
from .logging_setup import get_logger

logger = get_logger(__name__)

# Optional pydicom support
try:
    import pydicom  # type: ignore
    HAVE_PYDICOM = True
except Exception:
    HAVE_PYDICOM = False

@dataclass
class Group:
    key: str
    files: Set[Path] = field(default_factory=set)
    last_seen = now()
    created_at = now()

    def add(self, p: Path) -> None:
        self.files.add(p)
        self.last_seen = now()

class GroupManager:
    def __init__(self) -> None:
        self._groups: Dict[str, Group] = {}
        self._lock = __import__("threading").Lock()

    def add_file(self, key: str, p: Path) -> Group:
        with self._lock:
            g = self._groups.get(key)
            if not g:
                g = Group(key)
                self._groups[key] = g
            g.add(p)
            return g

    def harvest_ready(self, quiet_period_sec: float) -> List[Group]:
        ready: List[Group] = []
        with self._lock:
            quiet_cutoff = now() - timedelta(seconds=quiet_period_sec)
            for k, g in list(self._groups.items()):
                if g.last_seen < quiet_cutoff and g.files:
                    ready.append(g)
                    self._groups.pop(k, None)
        # close very old groups regardless
        cutoff = now() - timedelta(seconds=MAX_GROUP_AGE_SEC)
        too_old: List[Group] = []
        with self._lock:
            for k, g in list(self._groups.items()):
                if g.created_at < cutoff and g.files:
                    too_old.append(g)
                    self._groups.pop(k, None)
        return ready + too_old

GROUPS = GroupManager()

def derive_group_key(p: Path) -> str:
    if HAVE_PYDICOM:
        try:
            ds = pydicom.dcmread(str(p), stop_before_pixels=True, force=True)  # type: ignore[attr-defined]
            uid = getattr(ds, "StudyInstanceUID", None)
            if uid:
                return f"study:{uid}"
        except Exception:
            pass
    return f"folder:{p.parent.resolve()}"
