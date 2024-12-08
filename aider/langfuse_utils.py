# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges from upstream manually. See CONTRIBUTING.md.

"""Abstractions for Langfuse tracing.

This module provides a clean interface for all Langfuse operations. It manages configuration,
initialization, and provides methods for creating and managing traces. Key features:

- Initialization from environment variables or explicit configuration
- Context managers for clean trace/span lifecycle management
- Automatic handling of start/end times and exceptions
- Support for both sync and async contexts
- Clean abstractions for streaming responses
"""

import contextlib
import logging
import os
from dataclasses import dataclass
from typing import Any, Callable, Iterator, TypeVar

from langfuse import Langfuse
from langfuse.api.resources.commons.types.observation_level import ObservationLevel

logger = logging.getLogger(__name__)

T = TypeVar("T")  # For generic type hints


@dataclass
class LangfuseConfig:
    """Configuration for Langfuse client.

    This class encapsulates all configuration needed to initialize a Langfuse client.
    It supports both environment variables and explicit configuration.
    """

    public_key: str | None = None
    secret_key: str | None = None
    host: str = "https://cloud.langfuse.com"
    debug: bool = False


class LangfuseError(Exception):
    """Base class for Langfuse-related errors."""

    pass


class LangfuseConfigError(LangfuseError):
    """Raised when there are problems with Langfuse configuration."""

    pass


class LangfuseTracer:
    """Main class for managing Langfuse tracing.

    This class provides a clean interface for all Langfuse operations. It handles:
    - Client initialization and configuration
    - Trace and span lifecycle management
    - Error handling and logging
    - Streaming response handling

    The class uses context managers to ensure proper cleanup of resources and
    accurate timing information.

    Example:
        ```python
        tracer = LangfuseTracer()

        # Trace an LLM call
        with tracer.trace_generation(messages, model="gpt-4") as generation:
            response = llm.complete(messages)
            generation.end(output=response)

        # Trace a high-level operation
        with tracer.trace("process-document") as trace:
            result = process_document()
            trace.update(output=result)
        ```
    """

    def __init__(
        self,
        config: LangfuseConfig | None = None,
        on_error: Callable[[Exception], Any] | None = None,
    ):
        """Initialize the tracer.

        Args:
            config: Optional configuration object. If not provided, will use environment variables.
            on_error: Optional callback for handling errors. If not provided, errors are logged.

        Raises:
            LangfuseConfigError: If required configuration is missing or invalid.
        """
        if config is None:
            config = LangfuseConfig()

        self.config = config
        self.on_error = on_error or self._default_error_handler

        # Use environment variables as fallback
        self.public_key = config.public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = config.secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        self.host = config.host or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not self.public_key or not self.secret_key:
            raise LangfuseConfigError(
                "Langfuse public_key and secret_key are required. "
                "Set them via LangfuseConfig or environment variables."
            )

        logger.debug("Initializing Langfuse client with host %s", self.host)

        try:
            self.client = Langfuse(
                public_key=self.public_key,
                secret_key=self.secret_key,
                host=self.host,
            )
        except Exception as e:
            raise LangfuseConfigError(f"Failed to initialize Langfuse client: {e}") from e

    def _default_error_handler(self, e: Exception) -> None:
        """Default error handler that logs errors.

        Args:
            e: The exception that was caught
        """
        logger.error("Langfuse error: %s", str(e), exc_info=True)

    @contextlib.contextmanager
    def trace_generation(
        self,
        messages: list[dict[str, Any]],
        model: str,
        stream: bool = False,
        name: str = "generation",
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[Any]:
        """Create a trace for an LLM API call.

        This context manager handles the lifecycle of a generation trace, including:
        - Creating the trace and generation
        - Setting start/end times automatically
        - Handling errors appropriately
        - Supporting streaming responses
        - Capturing metadata

        Args:
            messages: The messages being sent to the LLM
            model: The name of the model being used
            stream: Whether this is a streaming call
            name: Name for the trace
            metadata: Optional metadata to attach to the generation

        Returns:
            A context manager that yields the generation object

        Raises:
            LangfuseError: If there are problems creating or updating the trace
        """
        logger.debug("Creating generation trace '%s' for model %s", name, model)

        try:
            trace = self.client.trace(name=name)
            generation = trace.generation(
                name=name,
                model=model,
                input=messages,
                metadata=metadata,
            )

            try:
                yield generation
            except Exception as e:
                logger.error("Error in generation trace '%s': %s", name, str(e), exc_info=True)
                generation.end(level=ObservationLevel.ERROR, status_message=str(e))
                raise
            finally:
                if not stream:
                    generation.end()

        except Exception as e:
            self.on_error(e)
            raise LangfuseError(f"Failed to manage generation trace: {e}") from e

    @contextlib.contextmanager
    def trace(
        self, name: str, metadata: dict[str, Any] | None = None, **kwargs: Any
    ) -> Iterator[Any]:
        """Create a trace for a high-level operation (as opposed to a generation).

        This context manager creates and manages a trace for any high-level operation.
        It supports arbitrary attributes via kwargs and handles cleanup automatically.

        Args:
            name: Name for the trace
            metadata: Optional metadata to attach to the trace
            **kwargs: Additional trace attributes

        Returns:
            A context manager that yields the trace object

        Raises:
            LangfuseError: If there are problems creating or updating the trace
        """
        logger.debug("Creating trace '%s'", name)

        try:
            trace = self.client.trace(name=name, metadata=metadata, **kwargs)
            try:
                yield trace
            except Exception as e:
                logger.error("Error in trace '%s': %s", name, str(e), exc_info=True)
                raise

        except Exception as e:
            self.on_error(e)
            raise LangfuseError(f"Failed to manage trace: {e}") from e

    def flush(self) -> None:
        """Flush any pending traces.

        This method ensures all pending traces are sent to Langfuse before the
        application exits. It should be called before shutdown in short-lived
        environments like serverless functions.

        Raises:
            LangfuseError: If there are problems flushing traces
        """
        logger.debug("Flushing pending traces")

        try:
            self.client.flush()
        except Exception as e:
            self.on_error(e)
            raise LangfuseError(f"Failed to flush traces: {e}") from e
