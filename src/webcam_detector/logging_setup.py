"""Logging configuration module for Webcam Object Detector."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys


def setup_logging(log_file_path: Path | None = None, level: int = logging.INFO) -> logging.Logger:
    """Configures application-wide logging with console and rotating file output.

    Args:
        log_file_path: Optional path to write log files. If None, defaults to
            ~/.local/state/webcam_detector/app.log
        level: Logging level (default logging.INFO).

    Returns:
        Root logger for webcam_detector.
    """
    logger = logging.getLogger("webcam_detector")
    logger.setLevel(level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file_path is None:
        state_dir = Path.home() / ".local" / "state" / "webcam_detector"
        state_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = state_dir / "app.log"
    else:
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=2 * 1024 * 1024,  # 2MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Failed to initialize file logger at {log_file_path}: {e}")

    logger.info("Logging initialized successfully.")
    return logger
