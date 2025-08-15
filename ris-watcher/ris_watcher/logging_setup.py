import sys, logging
from logging.handlers import RotatingFileHandler
from .config import LOG_DIR, LOG_LEVEL
LOG_FILE = LOG_DIR / "ris_watcher.log"
def get_logger(name: str = "RISWatcher") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(threadName)s | %(message)s")
    fh = RotatingFileHandler(LOG_FILE, maxBytes=10_000_000, backupCount=5)
    fh.setFormatter(fmt); fh.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    ch = logging.StreamHandler(sys.stdout); ch.setFormatter(fmt); ch.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    logger.addHandler(fh); logger.addHandler(ch); return logger
