"""Additional tests for logger JSON formatting and exception path."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from opengov_earlymathematics.utils.logger import get_logger
from opengov_earlymathematics import config


def test_logger_json_exception_path(tmp_path, monkeypatch):
    """Ensure JSON formatter handles exceptions without errors."""
    # Use a unique logger name to avoid handler reuse across tests
    logger = get_logger("json_exception_test")

    try:
        raise ValueError("boom")
    except ValueError:
        # This should include exc_info and exercise the JSONFormatter exception branch
        logger.exception("An error occurred while processing")

    # Calling a second time should reuse handlers (no duplication)
    logger2 = get_logger("json_exception_test")
    assert logger2 is logger


def test_logger_human_readable_formatter(monkeypatch):
    # Temporarily switch to non-json to hit human-readable formatter branch
    old = config.settings.log_format
    config.settings.log_format = "text"
    try:
        logger = get_logger("human_formatter_test")
        logger.info("hello")
    finally:
        config.settings.log_format = old
