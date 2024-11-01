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

# Configure logging for Langfuse error handling
logger = logging.getLogger(__name__)


class LangfuseErrorHandler:
    """Handles Langfuse-related errors to ensure they don't impact core functionality."""

    def __init__(self):
        self.error_count = 0
        self.max_errors = 3  # Maximum errors before disabling Langfuse
        self.disabled = False

    def handle_error(self, error, context):
        """Handle a Langfuse error.

        Args:
            error: The exception that occurred
            context: Optional dict with additional error context
        """
        self.error_count += 1

        # Log the error with context
        logger.warning(
            "Langfuse error occurred: %s. Context: %s", str(error), context or {}, exc_info=True
        )

        if self.error_count >= self.max_errors:
            self.disabled = True
            logger.warning(
                "Langfuse disabled after %d errors. Restart aider to re-enable.", self.max_errors
            )

    def is_disabled(self) -> bool:
        """Check if Langfuse should be disabled due to errors."""
        return self.disabled


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


litellm = LazyLiteLLM()


# Initialize Langfuse error handler
langfuse_error_handler = LangfuseErrorHandler()

# Configure Langfuse with error handling
try:
    langfuse_context.configure(
        error_handler=langfuse_error_handler,
        disable_on_error=True,  # Disable Langfuse if persistent errors occur
    )
except Exception as e:
    logger.warning("Failed to configure Langfuse: %s", str(e))

__all__ = [litellm]
