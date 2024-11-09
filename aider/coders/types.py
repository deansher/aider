# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

"""Shared type definitions used across both Aider and Brade style files.

This module defines the core types used throughout the codebase. These types are used:
- As type hints in Brade-style files
- In docstrings and comments in Aider-style files

This provides a consistent vocabulary for types across both coding styles while
preserving merge compatibility where needed.
"""

from typing import TypedDict


class ChatMessage(TypedDict):
    """A message in a chat conversation with an LLM.

    Attributes:
        role: The role of the message sender (system, user, assistant)
        content: The message content, either as a string or structured content
        function_call: Optional function call data
    """

    role: str  # "system", "user", "assistant"
    content: str | list["ContentBlock"]
    function_call: dict[str, str] | None


class ImageUrl(TypedDict):
    """Image data for a content block."""

    url: str  # Can be a web URL or data URL
    detail: str  # "low", "high", etc


class CacheControl(TypedDict):
    """Cache control metadata for a content block."""

    type: str  # "ephemeral" etc


class ContentBlock(TypedDict):
    """A block of structured content in a chat message.

    Can represent:
    - Simple text with optional cache control
    - Image data with URL and detail level
    """

    type: str  # "text" or "image_url"
    text: str | None  # Present for text blocks
    image_url: ImageUrl | None  # Present for image blocks
    cache_control: CacheControl | None


class EditBlock(TypedDict):
    """A code edit block extracted from an LLM response.

    Attributes:
        path: The file path to edit, None for other actions
        content: The edit content or action description
    """

    path: str | None
    content: str


class RepoFile(TypedDict):
    """Information about a file in the repository.

    Attributes:
        path: The file path relative to repo root
        content: The file content if available
        size: File size in bytes
    """

    path: str
    content: str | None
    size: int
