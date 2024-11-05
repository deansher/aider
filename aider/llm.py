import importlib
import logging
import os
import warnings

from langfuse.decorators import langfuse_context

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

AIDER_SITE_URL = "https://aider.chat"
AIDER_APP_NAME = "Aider"

os.environ["OR_SITE_URL"] = AIDER_SITE_URL
os.environ["OR_APP_NAME"] = AIDER_APP_NAME
os.environ["LITELLM_MODE"] = "PRODUCTION"

logger = logging.getLogger(__name__)


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

        # Configure Langfuse after environment variables are loaded
        try:
            langfuse_context.configure()
        except Exception as e:
            logger.warning("Failed to configure Langfuse: %s", str(e))


litellm = LazyLiteLLM()


__all__ = [litellm]
