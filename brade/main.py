import logging
import sys

import aider
from aider.main import main as aider_main
from aider.utils import get_log_file


def setup_file_logging():
    log_file = get_log_file()
    file_handler = logging.FileHandler(str(log_file), encoding="utf-8")

    # The handler can handle debug logs if they're passed to it
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Set the root logger to INFO, so it discards debug by default
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)


# Call our setup before we do anything else
setup_file_logging()


logger = logging.getLogger(__name__)  # This picks up the new file-based logging

# TODO: Re-enable bug reporting with these enhancements:
# 1. Report bugs to the brade project instead of aider
# 2. Add a command-line argument / configuration parameter to disable it
# 3. Consider raising errors in development mode


def main():
    logger.debug("Executing brade's main entry point.")
    logger.debug(f"Using aider module from: {aider.__file__}")
    return aider_main()


if __name__ == "__main__":
    status = main()
    sys.exit(status)
