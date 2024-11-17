import importlib
import logging
import os
import warnings

from langfuse import Langfuse
from langfuse.decorators import langfuse_context

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

BRADE_SITE_URL = "https://github.com/deansher/brade"
BRADE_APP_NAME = "Brade"

os.environ["OR_SITE_URL"] = BRADE_SITE_URL
os.environ["OR_APP_NAME"] = BRADE_APP_NAME
os.environ["LITELLM_MODE"] = "PRODUCTION"

logger = logging.getLogger(__name__)

# Flag to track Langfuse status
langfuse_enabled = True
langfuse_instance = None


# `import litellm` takes 1.5 seconds, defer it!
class LazyLiteLLM:
    _lazy_module = None

    def __getattr__(self, name):
        if name == "_lazy_module":
            return super()
        self._load_litellm()
        return getattr(self._lazy_module, name)

    def _load_litellm(self):
        if self._lazy_module is not None:
            return

        self._lazy_module = importlib.import_module("litellm")

        self._lazy_module.suppress_debug_info = True
        self._lazy_module.set_verbose = False
        self._lazy_module.drop_params = True
        self._lazy_module._logging._disable_debugging()

        # Check if we're running in a test environment
        global langfuse_enabled
        if "PYTEST_CURRENT_TEST" in os.environ:
            langfuse_enabled = False
            logger.debug("Langfuse disabled in test environment")
            return

        # Configure Langfuse after environment variables are loaded
        try:
            if langfuse_enabled:
                langfuse_context.configure()
                global langfuse_instance
                langfuse_instance = Langfuse()
        except Exception as e:
            langfuse_enabled = False
            logger.info("Langfuse disabled: %s", str(e))


litellm = LazyLiteLLM()


__all__ = [litellm]
