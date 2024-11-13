import logging
import sys

import aider
from aider.main import main as aider_main

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
