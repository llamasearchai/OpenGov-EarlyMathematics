"""Logging utilities for OpenGov-EarlyMathematics."""

import logging
import sys
from typing import Optional

from opengov_earlymathematics.config import settings


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a logger instance with the specified name and level."""
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Set level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Create formatter
    if settings.log_format == "json":
        import datetime
        import json

        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }

                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)

                return json.dumps(log_entry)

    else:
        # Human-readable format
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter if settings.log_format != "json" else JSONFormatter())
    logger.addHandler(console_handler)

    # File handler for errors and above
    if settings.log_level.upper() in ["ERROR", "WARNING", "INFO", "DEBUG"]:
        file_handler = logging.FileHandler("app.log")
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter if settings.log_format != "json" else JSONFormatter())
        logger.addHandler(file_handler)

    return logger
