import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "pipeline.log"

def get_logger(name: str = "pipeline_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate log handlers
    if not logger.handlers:
        # File handler with rotation (5MB, 3 backups)
        fh = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
        fh.setLevel(logging.DEBUG)
        fh_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch_formatter = logging.Formatter('%(levelname)s | %(message)s')
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)

    return logger
