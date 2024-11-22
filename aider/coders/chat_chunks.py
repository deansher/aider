# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

from dataclasses import dataclass, field

from ..types import ChatMessage


@dataclass
class ChatChunks:
    """Manages the organization and formatting of chat message chunks for LLM interactions.

    This class has three responsibilities:

    - It provides a place to organize context needed for generating an LLLM prompt.
      Each chunk of content is represented as a list of messages.
    - It chooses how to order those messages when it returns them from all_messages().
    - It places cache control directives on its choice of messages when
      `add_cache_control()` is called.

    The following chunks are managed:

    - `system`: System messages - Core instructions and role definition
    - `examples`: Examples - Sample conversations demonstrating desired behavior
    - `readonly_files`: Read-only files - Reference material not to be modified
    - `repo`: Repository content - Code files and structure
    - `done`: Done messages - Previous conversation history
    - `chat_files`: Chat files - Files currently being edited
    - `cur`: Current messages - Active conversation
    - `reminder`: Reminder messages - Additional context/instructions
    """

    system: list[ChatMessage] = field(default_factory=list)
    examples: list[ChatMessage] = field(default_factory=list)
    done: list[ChatMessage] = field(default_factory=list)
    repo: list[ChatMessage] = field(default_factory=list)
    readonly_files: list[ChatMessage] = field(default_factory=list)
    chat_files: list[ChatMessage] = field(default_factory=list)
    cur: list[ChatMessage] = field(default_factory=list)
    reminder: list[ChatMessage] = field(default_factory=list)

    def all_messages(self) -> list[ChatMessage]:
        """Concatenates all message chunks in a chosen but unspecified order."""
        return (
            self.system
            + self.examples
            + self.readonly_files
            + self.repo
            + self.done
            + self.chat_files
            + self.cur
            + self.reminder
        )

    def add_cache_control_headers(self) -> None:
        """Adds cache control headers to appropriate message chunks.

        Modifies messages in place to add cache control headers that enable
        prompt caching optimizations. Headers are added to:
        - Examples (or system if no examples)
        - Repository content (which includes readonly files)
        - Chat files
        """
        if self.examples:
            self.add_cache_control(self.examples)
        else:
            self.add_cache_control(self.system)

        if self.repo:
            # this will mark both the readonly_files and repomap chunk as cacheable
            self.add_cache_control(self.repo)
        else:
            # otherwise, just cache readonly_files if there are any
            self.add_cache_control(self.readonly_files)

        self.add_cache_control(self.chat_files)

    def add_cache_control(self, messages: list[ChatMessage]) -> None:
        """Adds cache control header to the last message in a message list.

        Modifies the last message in the provided list to include cache control
        headers that enable prompt caching optimizations. Handles both string
        and dictionary content formats.

        Args:
            messages: List of message dictionaries to modify
        """
        if not messages:
            return

        content = messages[-1]["content"]
        if isinstance(content, str):
            content = dict(
                type="text",
                text=content,
            )
        content["cache_control"] = {"type": "ephemeral"}

        messages[-1]["content"] = [content]

    def cacheable_messages(self) -> list[ChatMessage]:
        """Returns the subset of messages that can be cached.

        Examines all messages in reverse order to find the last message with
        cache control headers. Returns all messages up to and including that
        message, as these form a cacheable unit.

        Returns:
            list[dict[str, Any]]: Messages that can be cached as a unit
        """
        messages = self.all_messages()
        for i, message in enumerate(reversed(messages)):
            if isinstance(message.get("content"), list) and message["content"][0].get(
                "cache_control"
            ):
                return messages[: len(messages) - i]
        return messages
