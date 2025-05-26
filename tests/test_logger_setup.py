import logging
import tempfile
import os
import sys
import pytest
import importlib.util

spec = importlib.util.spec_from_file_location(
    "logger_setup",
    os.path.join(os.path.dirname(__file__),
                 "../src/infrastructure/logger_setup.py")
)
logger_setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_setup)
setup_logging = logger_setup.setup_logging
DEFAULT_LOG_LEVEL = logger_setup.DEFAULT_LOG_LEVEL


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "invalid"])
def test_setup_logging_sets_level_and_handlers(level):
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "test.log")
        setup_logging(log_level=level, log_file_path=log_path)
        root_logger = logging.getLogger()
        expected_level = level.upper() if level.upper() in [
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] else DEFAULT_LOG_LEVEL
        assert logging.getLevelName(root_logger.level) == expected_level
        assert len(root_logger.handlers) == 2
        for handler in root_logger.handlers:
            fmt = handler.formatter._fmt
            assert "%(asctime)s" in fmt and "%(levelname)s" in fmt and "%(message)s" in fmt
        file_handlers = [
            h for h in root_logger.handlers if hasattr(h, "baseFilename")]
        assert any(h.baseFilename == log_path for h in file_handlers)


def test_logging_output_to_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "test2.log")
        setup_logging(log_level="DEBUG", log_file_path=log_path)
        logger = logging.getLogger("test.module")
        logger.debug("debug message")
        logger.error("error message")
        for h in logging.getLogger().handlers:
            h.flush()
        with open(log_path, encoding="utf-8") as f:
            content = f.read()
        assert "debug message" in content
        assert "error message" in content
        assert "test.module" in content
        assert "DEBUG" in content and "ERROR" in content


def test_logging_exception_with_stack_trace():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "exception.log")
        setup_logging(log_level="ERROR", log_file_path=log_path)
        logger = logging.getLogger("exception.test")
        try:
            raise ValueError("This is a test exception")
        except ValueError:
            logger.error("An exception occurred", exc_info=True)
        for h in logging.getLogger().handlers:
            h.flush()
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "ERROR" in content
        assert "An exception occurred" in content
        assert "Traceback (most recent call last):" in content
        assert 'raise ValueError("This is a test exception")' in content
