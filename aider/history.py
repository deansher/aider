# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

from typing import Optional

from aider import models, prompts
from aider.dump import dump  # noqa: F401
from aider.io import InputOutput
from aider.sendchat import simple_send_with_retries
from aider.types import ChatMessage, TokenCountFunc


class ChatSummary:
    """Manages summarization of chat history to keep it within token limits.

    This class handles the recursive summarization of chat history when it grows too large.
    It uses a divide-and-conquer approach for large histories and preserves more recent
    messages when possible.

    Attributes:
        models: List of Model instances to use for summarization, tried in order
        max_tokens: Maximum number of tokens allowed in resuling history
        token_count: Function from first model used to count tokens in messages
    """

    def __init__(
        self,
        models: Optional[models.Model | list[models.Model]] = None,
        max_tokens: int = 1024,
        io: Optional[InputOutput] = None,
        label: Optional[str] = None,
    ) -> None:
        """Initialize a ChatSummary instance.

        Args:
            models: One or more Model instances to use for summarization.
                   Models are tried in order if earlier ones fail.
            max_tokens: Maximum number of tokens allowed in summarized history.
                       Default is 1024.
            io: Optional InputOutput instance for logging summarization progress.
            label: Optional label to prefix log messages with.

        Raises:
            ValueError: If no models are provided.
        """
        if not models:
            raise ValueError("At least one model must be provided")
        self.models = models if isinstance(models, list) else [models]
        self.max_tokens = max_tokens
        self.token_count: TokenCountFunc = self.models[0].token_count
        self.io = io
        self.label = label
        self._prefix = f"[{self.label}] " if self.label else ""

    def _format_message_preview(self, tokens: int, msg: ChatMessage) -> str:
        """Format a message preview with token count, role, and content.

        Args:
            tokens: Number of tokens in the message
            msg: The chat message to preview

        Returns:
            Formatted string with fixed-width fields for token count and role,
            followed by first 30 chars of content
        """
        preview = msg["content"][:30]
        return f"{tokens:6,} tokens  {msg['role']:10} {preview}"

    def too_big(self, messages: list[ChatMessage]) -> bool:
        """Check if messages exceed the token limit.

        Args:
            messages: List of chat messages to check.

        Returns:
            True if total tokens exceeds max_tokens, False otherwise.
        """
        sized = self.tokenize(messages)
        total = sum(tokens for tokens, _msg in sized)
        if self.io:
            self.io.tool_output(
                f"{self._prefix}Checking message size: {total:,} tokens vs limit of"
                f" {self.max_tokens:,}"
            )
        return total > self.max_tokens

    def tokenize(self, messages: list[ChatMessage]) -> list[tuple[int, ChatMessage]]:
        """Count tokens in each message.

        Args:
            messages: List of chat messages to tokenize.

        Returns:
            List of (token_count, message) tuples.
        """
        sized = []
        for msg in messages:
            tokens = self.token_count(msg)
            sized.append((tokens, msg))
        return sized

    def summarize(self, messages: list[ChatMessage], recursion_depth: int = 0) -> list[ChatMessage]:
        """Summarize messages as necessary to fit within token limit.

        This method uses a divide-and-conquer approach to summarize chat history:
        1. If messages fit in token limit, return them unchanged
        2. If messages are too small to split, summarize everything
        3. Otherwise split messages and recursively process each part:
           - Find split point that preserves recent messages
           - Summarize older messages while preserving newer ones
           - Combine and check if result fits in token limit
           - If still too large, recurse on combined result

        Args:
            messages: List of chat messages to summarize
            recursion_depth: Current recursion depth, used to limit recursion

        Returns:
            List of messages that fit within self.max_tokens

        Raises:
            ValueError: If no models are available for summarization
        """
        # Validate models and check if summarization is needed
        if not self.models:
            raise ValueError("No models available for summarization")

        sized = self.tokenize(messages)
        total = sum(tokens for tokens, _msg in sized)
        if total <= self.max_tokens and recursion_depth == 0:
            return messages

        if self.io:
            self.io.tool_output(
                f"\n{self._prefix}Summarizing as necessary from {len(messages):,} messages with"
                f" {total:,} tokens"
            )

        # Handle base cases: too small to split or max recursion reached
        min_split = 4
        if len(messages) <= min_split or recursion_depth > 3:
            return self.summarize_all(messages)

        # Find initial split point targeting half of max tokens for tail
        tail_tokens = 0
        split_index = len(messages)
        half_max_tokens = self.max_tokens // 2

        if self.io:
            self.io.tool_output(
                f"\n{self._prefix}Finding split point targeting {half_max_tokens:,} tokens for tail"
            )

        for i in range(len(sized) - 1, -1, -1):
            tokens, _msg = sized[i]
            if tail_tokens + tokens < half_max_tokens:
                tail_tokens += tokens
                split_index = i
                if self.io:
                    self.io.tool_output(
                        f"{self._prefix}Including message {i} in tail, now at"
                        f" {tail_tokens:,} tokens"
                    )
            else:
                break

        # Adjust split point to ensure clean conversation breaks
        while messages[split_index - 1]["role"] != "assistant" and split_index > 1:
            split_index -= 1
            if self.io:
                self.io.tool_output(
                    f"{self._prefix}Adjusting split point to {split_index} to get clean break"
                )

        if split_index <= min_split:
            return self.summarize_all(messages)

        # Split messages into a head and tail. Then select messages from head
        # to keep and summarize.
        head = messages[:split_index]
        tail = messages[split_index:]

        sized = sized[:split_index]
        head.reverse()  # temporarily for convenience
        sized.reverse()
        keep = []
        total = 512  # Reserve space for summarization system prompt

        # Calculate how many older messages we can keep
        model_max_input_tokens = self.models[0].info.get("max_input_tokens") or 4096

        if self.io:
            self.io.tool_output(
                f"\n{self._prefix}Keeping messages up to {model_max_input_tokens:,} tokens"
            )

        for i in range(split_index):
            total += sized[i][0]
            if total > model_max_input_tokens:
                if self.io:
                    self.io.tool_output(f"{self._prefix}Stopping at {total:,} tokens")
                break
            keep.append(head[i])
            if self.io:
                self.io.tool_output(f"{self._prefix}Keeping message {i}, now at {total:,} tokens")

        keep.reverse()  # restore forward order

        # Summarize head and combine with tail
        summary = self.summarize_all(keep)
        tail_tokens = sum(tokens for tokens, msg in sized[split_index:])
        summary_tokens = self.token_count(summary)

        # Check if combined result fits in token limit
        result = summary + tail
        if summary_tokens + tail_tokens < self.max_tokens:
            # Show summarized and remaining messages if some were summarized away
            if self.io and len(summary) < len(keep):
                self.io.tool_output(f"\n{self._prefix}Messages that were summarized away:")
                for msg in keep[len(summary) :]:
                    self.io.tool_output(self._format_message_preview(self.token_count(msg), msg))

                self.io.tool_output(f"\n{self._prefix}Messages that remain:")
                for msg in result:
                    self.io.tool_output(self._format_message_preview(self.token_count(msg), msg))

            return result

        # If still too large, recurse on combined result
        return self.summarize(result, recursion_depth + 1)

    def summarize_all(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        """Summarize all messages into a single summary message.

        Formats messages into a markdown-like format and sends to LLM for summarization.
        Tries each model in sequence until one succeeds.

        Args:
            messages: List of chat messages to summarize

        Returns:
            List containing a single summary message

        Raises:
            ValueError: If summarization fails for all available models
        """
        if self.io:
            self.io.tool_output(f"\n{self._prefix}Summarizing {len(messages):,} messages")
        content = ""
        for msg in messages:
            role = msg["role"].upper()
            if role not in ("USER", "ASSISTANT"):
                continue
            content += f"# {role}\n"
            msg_content = msg["content"]
            if isinstance(msg_content, list):
                for block in msg_content:
                    if block.get("type") == "text" and block.get("text"):
                        content += block["text"] or ""
            else:
                content += msg_content
            if not content.endswith("\n"):
                content += "\n"
        summarize_messages = [
            dict(role="system", content=prompts.summarize),
            dict(role="user", content=content),
        ]

        for model in self.models:
            try:
                summary = simple_send_with_retries(
                    model.name,
                    summarize_messages,
                    extra_params=model.extra_params,
                    purpose="summarize old messages",
                )
                if summary is not None:
                    summary = prompts.summary_prefix + summary
                    return [dict(role="user", content=summary)]
            except Exception as e:
                print(f"Summarization failed for model {model.name}: {str(e)}")

        raise ValueError("summarizer unexpectedly failed for all models")
