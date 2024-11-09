# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

"""Shared type definitions used across both Aider and Brade style files.

This module defines the core types used throughout the codebase. These types are used:
- As type hints in Brade-style files
- In docstrings and comments in Aider-style files

This provides a consistent vocabulary for types across both coding styles while
preserving merge compatibility where needed.
"""

from typing import Any, TypedDict


class ChatMessage(TypedDict):
    """A message in a chat conversation with an LLM.
    
    Attributes:
        role: The role of the message sender (system, user, assistant)
        content: The message content, either as a string or structured content
    """
    role: str
    content: str | list[dict[str, Any]]


class EditBlock(TypedDict):
    """A code edit block extracted from an LLM response.
    
    Attributes:
        path: The file path to edit
        search: The text to search for
        replace: The text to replace it with
    """
    path: str
    search: str 
    replace: str


class RepoFile(TypedDict):
    """Information about a file in the repository.
    
    Attributes:
        path: The file path relative to repo root
        content: The file content if available
        summary: A summary of the file's purpose
    """
    path: str
    content: str | None
    summary: str | None
