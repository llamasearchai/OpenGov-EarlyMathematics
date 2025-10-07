"""Unit tests for logger."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from opengov_earlymathematics.utils.logger import get_logger


class TestLogger:
    """Test logger utility."""

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger(__name__)
        assert logger is not None
        assert logger.name == __name__

    def test_get_logger_different_names(self):
        """Test getting loggers with different names."""
        logger1 = get_logger("test1")
        logger2 = get_logger("test2")
        assert logger1.name == "test1"
        assert logger2.name == "test2"
        assert logger1 is not logger2

    def test_logger_methods_exist(self):
        """Test that logger has required methods."""
        logger = get_logger(__name__)
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "debug")

    def test_logger_can_log(self):
        """Test that logger can log messages."""
        logger = get_logger(__name__)
        # Should not raise an exception
        logger.info("Test info message")
        logger.error("Test error message")
        logger.warning("Test warning message")
        logger.debug("Test debug message")
