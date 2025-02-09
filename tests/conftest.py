import io
import logging
import pytest


@pytest.fixture
def capture_logs():
    """Fixture to capture log output during tests.

    This fixture:
    1. Sets up a StringIO buffer to capture logs
    2. Configures logging to write to that buffer
    3. Makes the buffer available to the test
    4. Cleans up after the test

    Usage:
        def test_something(capture_logs):
            # Do something that logs
            assert "expected message" in capture_logs.getvalue()
    """
    log_buffer = io.StringIO()
    handler = logging.StreamHandler(log_buffer)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
        )
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)

    yield log_buffer

    root_logger.removeHandler(handler)
    log_buffer.close()
