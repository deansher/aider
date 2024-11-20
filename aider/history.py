# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

import argparse
from typing import Optional

from aider import models, prompts
from aider.coders.types import ChatMessage
from aider.dump import dump  # noqa: F401
from aider.sendchat import simple_send_with_retries


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
        max_tokens: int = 1024
    ) -> None:
        """Initialize a ChatSummary instance.
        
        Args:
            models: One or more Model instances to use for summarization.
                   Models are tried in order if earlier ones fail.
            max_tokens: Maximum number of tokens allowed in summarized history.
                       Default is 1024.
                
        Raises:
            ValueError: If no models are provided.
        """
        if not models:
            raise ValueError("At least one model must be provided")
        self.models = models if isinstance(models, list) else [models]
        self.max_tokens = max_tokens
        self.token_count = self.models[0].token_count

    def too_big(self, messages: list[ChatMessage]) -> bool:
        """Check if messages exceed the token limit.
        
        Args:
            messages: List of chat messages to check.
            
        Returns:
            True if total tokens exceeds max_tokens, False otherwise.
        """
        sized = self.tokenize(messages)
        total = sum(tokens for tokens, _msg in sized)
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

    def summarize(
        self, messages: list[ChatMessage], depth: int = 0
    ) -> list[ChatMessage]:
        """Recursively summarize messages to fit within token limit.
        
        Uses a divide-and-conquer approach for large message histories:
        1. If messages fit within limit and depth=0, return unchanged
        2. If messages are small or depth>3, summarize all messages
        3. Otherwise:
           - Split messages roughly in half
           - Ensure split point is after an assistant message
           - Keep recent messages that fit within model's context window
           - Recursively summarize older messages if needed
        
        Args:
            messages: List of chat messages to summarize
            depth: Current recursion depth, used to limit recursion
            
        Returns:
            List of summarized messages that fit within token limit
            
        Raises:
            ValueError: If no models are available for summarization
        """
        if not self.models:
            raise ValueError("No models available for summarization")

        sized = self.tokenize(messages)
        total = sum(tokens for tokens, _msg in sized)
        if total <= self.max_tokens and depth == 0:
            return messages

        min_split = 4
        if len(messages) <= min_split or depth > 3:
            return self.summarize_all(messages)

        tail_tokens = 0
        split_index = len(messages)
        half_max_tokens = self.max_tokens // 2

        # Iterate over the messages in reverse order
        for i in range(len(sized) - 1, -1, -1):
            tokens, _msg = sized[i]
            if tail_tokens + tokens < half_max_tokens:
                tail_tokens += tokens
                split_index = i
            else:
                break

        # Ensure the head ends with an assistant message
        while messages[split_index - 1]["role"] != "assistant" and split_index > 1:
            split_index -= 1

        if split_index <= min_split:
            return self.summarize_all(messages)

        head = messages[:split_index]
        tail = messages[split_index:]

        sized = sized[:split_index]
        head.reverse()
        sized.reverse()
        keep = []
        total = 0

        # These sometimes come set with value = None
        model_max_input_tokens = self.models[0].info.get("max_input_tokens") or 4096
        model_max_input_tokens -= 512

        for i in range(split_index):
            total += sized[i][0]
            if total > model_max_input_tokens:
                break
            keep.append(head[i])

        keep.reverse()

        summary = self.summarize_all(keep)

        tail_tokens = sum(tokens for tokens, msg in sized[split_index:])
        summary_tokens = self.token_count(summary)

        result = summary + tail
        if summary_tokens + tail_tokens < self.max_tokens:
            return result

        return self.summarize(result, depth + 1)

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
        content = ""
        for msg in messages:
            role = msg["role"].upper()
            if role not in ("USER", "ASSISTANT"):
                continue
            content += f"# {role}\n"
            content += msg["content"]
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


def main() -> None:
    """Command-line interface for chat history summarization.
    
    Parses a markdown file containing chat history and summarizes it using
    the ChatSummary class with default models.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Markdown file to parse")
    args = parser.parse_args()

    model_names = ["gpt-3.5-turbo", "gpt-4"]  # Add more model names as needed
    model_list = [models.Model(name) for name in model_names]
    summarizer = ChatSummary(model_list)

    with open(args.filename, "r") as f:
        text = f.read()

    summary = summarizer.summarize_chat_history_markdown(text)
    dump(summary)


if __name__ == "__main__":
    main()
