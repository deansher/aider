"""Brade's abstractions for Langfuse tracing.

This module provides a clean interface for all Langfuse operations in Brade.
It manages configuration, initialization, and provides methods for creating
and managing traces.
"""

import contextlib
import logging
import os
from typing import Any, Dict, Iterator, Optional

from langfuse import Langfuse

logger = logging.getLogger(__name__)


class LangfuseTracer:
    """Main class for managing Langfuse tracing in Brade.
    
    This provides a clean interface for all our Langfuse operations.
    It manages configuration, initialization, and provides methods
    for creating and managing traces.
    """
    
    def __init__(self, public_key: Optional[str] = None, secret_key: Optional[str] = None,
                 host: Optional[str] = None):
        """Initialize the tracer.
        
        Args:
            public_key: Optional Langfuse public key. If not provided, will use LANGFUSE_PUBLIC_KEY env var.
            secret_key: Optional Langfuse secret key. If not provided, will use LANGFUSE_SECRET_KEY env var.
            host: Optional Langfuse host. If not provided, will use LANGFUSE_HOST env var.
        """
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY") 
        self.host = host or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        self.client = Langfuse(
            public_key=self.public_key,
            secret_key=self.secret_key,
            host=self.host
        )
        
    @contextlib.contextmanager
    def trace_llm_call(self, messages: list, model: str, stream: bool = False,
                      name: str = "llm-call") -> Iterator[Any]:
        """Create a trace for an LLM API call.
        
        Args:
            messages: The messages being sent to the LLM
            model: The name of the model being used
            stream: Whether this is a streaming call
            name: Name for the trace
            
        Returns:
            A context manager that yields the trace object
        """
        trace = self.client.trace(name=name)
        generation = trace.generation(
            name=name,
            model=model,
            input=messages
        )
        
        try:
            yield generation
        except Exception as e:
            generation.end(
                level="ERROR",
                status_message=str(e)
            )
            raise
        finally:
            if not stream:
                generation.end()
    
    @contextlib.contextmanager  
    def trace_operation(self, name: str, **kwargs) -> Iterator[Any]:
        """Create a trace for a high-level operation.
        
        Args:
            name: Name for the trace
            **kwargs: Additional trace attributes
            
        Returns:
            A context manager that yields the trace object
        """
        trace = self.client.trace(name=name, **kwargs)
        try:
            yield trace
        finally:
            pass  # Traces don't need to be ended
            
    def flush(self):
        """Flush any pending traces."""
        self.client.flush()
