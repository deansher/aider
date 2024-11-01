import logging
import sys

import aider
from aider.main import main as aider_main

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.debug("Executing brade's main entry point.")
    logger.debug(f"Using aider module from: {aider.__file__}")
    return aider_main()


if __name__ == "__main__":
    status = main()
    sys.exit(status)
