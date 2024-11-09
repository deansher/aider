# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatChunks:
    """Manages the organization and formatting of chat message chunks for LLM interactions.
    
    This class structures the various components of a chat conversation with an LLM,
    including system context, examples, repository content, and current messages.
    It works closely with base_coder.py to maintain the chat state and format messages
    appropriately for the LLM.
    
    The message chunks are organized in a specific order to provide proper context:
    1. System messages - Core instructions and role definition
    2. Examples - Sample conversations demonstrating desired behavior
    3. Read-only files - Reference material not to be modified
    4. Repository content - Code files and structure
    5. Done messages - Previous conversation history
    6. Chat files - Files currently being edited
    7. Current messages - Active conversation
    8. Reminder messages - Additional context/instructions
    
    Each field is a list of message dictionaries with 'role' and 'content' keys,
    following the standard LLM chat message format.
    """
    system: list[dict[str, Any]] = field(default_factory=list)
    examples: list[dict[str, Any]] = field(default_factory=list)
    done: list[dict[str, Any]] = field(default_factory=list)
    repo: list[dict[str, Any]] = field(default_factory=list)
    readonly_files: list[dict[str, Any]] = field(default_factory=list)
    chat_files: list[dict[str, Any]] = field(default_factory=list)
    cur: list[dict[str, Any]] = field(default_factory=list)
    reminder: list[dict[str, Any]] = field(default_factory=list)

    def all_messages(self) -> list[dict[str, Any]]:
        """Combines all message chunks in the proper order for LLM context.
        
        Returns:
            A single list of message dictionaries containing all chunks in the order:
            system, examples, readonly_files, repo, done, chat_files, cur, and reminder.
            This ordering ensures proper context flow from general to specific.
        """
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

    def wrap_xml(self, tag: str, content: Any) -> str:
        """Wraps content in XML-style tags for structured message formatting.
        
        Args:
            tag: The XML tag name to wrap the content in
            content: The content to wrap (converted to string)
            
        Returns:
            The content wrapped in XML tags, or empty string if content is empty
        """
        if not content:
            return ""
        return f"<{tag}>\n{content}\n</{tag}>"

    def format_xml_messages(self) -> str:
        """Formats all message chunks as a structured XML document.
        
        Converts each message chunk into an XML section with appropriate tags
        based on the chunk's role in the conversation. Only includes non-empty
        chunks. The XML structure helps the LLM understand the different
        components of context.
        
        Returns:
            A string containing all non-empty message chunks formatted as XML sections
        """
        xml = []

        # System context
        if self.system:
            xml.append(self.wrap_xml("system_context", self.system[-1]["content"]))

        # Repository map
        if self.repo:
            xml.append(self.wrap_xml("repository_map", self.repo[-1]["content"]))

        # Project files
        if self.chat_files:
            xml.append(self.wrap_xml("project_files", self.chat_files[-1]["content"]))

        # Read-only files
        if self.readonly_files:
            xml.append(self.wrap_xml("readonly_files", self.readonly_files[-1]["content"]))

        # Instructions
        if self.reminder:
            xml.append(self.wrap_xml("instructions", self.reminder[-1]["content"]))

        # Current messages
        if self.cur:
            xml.append(self.wrap_xml("current_messages", self.cur[-1]["content"]))

        return "\n".join(xml)

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

    def add_cache_control(self, messages: list[dict[str, Any]]) -> None:
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

    def cacheable_messages(self) -> list[dict[str, Any]]:
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
