# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

from typing import Any

from aider.types import ChatMessage

from ..sendchat import analyze_assistant_response
from .architect_prompts import (
    APPROVED_NON_PLAN_CHANGES_PROMPT,
    APPROVED_PLAN_CHANGES_PROMPT,
    CHANGES_COMMITTED_MESSAGE,
    REVIEW_CHANGES_PROMPT,
    ArchitectPrompts,
    architect_proposed_non_plan_changes,
    architect_proposed_plan_changes,
    possible_architect_responses,
)
from .base_coder import Coder


class ArchitectExchange:
    """Encapsulates a complete architect-editor-reviewer exchange.

    This class maintains the sequence of messages that occur during an exchange between:
    - The architect proposing changes
    - The editor implementing changes
    - The reviewer validating changes

    Messages are appended to self.messages as they occur.
    """

    def __init__(self, architect_response: str):
        """Initialize a new exchange.

        Args:
            architect_response: The architect's response proposing changes
        """
        self.messages: list[ChatMessage] = [
            ChatMessage(role="assistant", content=architect_response)
        ]

    def append_editor_prompt(self, is_plan_change: bool) -> str:
        """Append the appropriate editor prompt based on whether this is a plan change.

        Args:
            is_plan_change: Whether this exchange involves changing a plan document

        Returns:
            The editor prompt that was appended
        """
        prompt = (
            APPROVED_PLAN_CHANGES_PROMPT if is_plan_change else APPROVED_NON_PLAN_CHANGES_PROMPT
        )
        self.messages.append(ChatMessage(role="user", content=prompt))
        return prompt

    def append_editor_response(self, response: str) -> None:
        """Append the editor's response implementing changes.

        Args:
            response: The editor's response after implementing changes
        """
        self.messages.append(ChatMessage(role="assistant", content=response))

    def append_reviewer_prompt(self) -> str:
        """Append and return the reviewer prompt."""
        self.messages.append(ChatMessage(role="user", content=REVIEW_CHANGES_PROMPT))
        return REVIEW_CHANGES_PROMPT

    def append_reviewer_response(self, response: str) -> None:
        """Append the reviewer's response validating changes.

        Args:
            response: The reviewer's response after validating changes
        """
        self.messages.append(ChatMessage(role="assistant", content=response))

    def get_messages(self) -> list[ChatMessage]:
        """Get all messages in the exchange.

        Returns:
            List of all messages that have occurred
        """
        return self.messages

    def has_editor_response(self) -> bool:
        """Check if the exchange includes an editor response.

        Returns:
            True if the exchange includes an editor response
        """
        return len(self.messages) >= 3  # Architect + editor prompt + editor response


class ArchitectCoder(Coder):
    """Manages high-level code architecture decisions and coordinates with editor/reviewer coders.

    This coder acts as an architect that:
    1. Analyzes requests and proposes changes
    2. Coordinates with editor coder to implement changes
    3. Coordinates with reviewer coder to validate changes

    Attributes:
        edit_format: The edit format identifier for this coder type
        produces_code_edits: Whether this coder directly produces code edits
        gpt_prompts: The prompts configuration for this coder
    """

    # Implementation Notes:
    #
    # We don't extend ArchitectCoder's chat history until the entire exchange is complete.
    #
    # When we create a subordinate model (editor or reviewer), it inherits the architect's
    # chat history. We extend the subordinate's chat history to include the messages that have
    # occurred so far in the exchange. We then capture the subordinate's response message
    # in the ArchitectExchange object for use by the next subordinate or for recording the entire
    # exchange at the end.

    edit_format = "architect"
    produces_code_edits = False  # Architect coder doesn't produce code edits directly
    gpt_prompts = ArchitectPrompts()

    def create_coder(self, edit_format: str, **kwargs: Any) -> Coder:
        """Creates a new coder instance from this architect coder.

        Args:
            coder_class: The coder class to instantiate
            **kwargs: Additional keyword arguments to override settings from this coder

        Returns:
            A configured coder instance inheriting base configuration (possibly modified
            by kwargs), message history, repo and file state, and possibly other state
            from this architect coder.
        """
        # Start with base config that overrides key settings
        use_kwargs = dict(
            suggest_shell_commands=False,
            map_tokens=0,
            cache_prompts=False,
            num_cache_warming_pings=0,
            edit_format=edit_format,
        )

        # Update with any passed kwargs
        use_kwargs.update(kwargs)

        # Create new coder that inherits parameters and state from this one
        coder = Coder.create(
            from_coder=self,
            summarize_from_coder=False,  # Preserve message history exactly
            **use_kwargs,
        )

        return coder

    def reply_completed(self) -> None:
        """Process the architect's response and coordinate with editor/reviewer as needed.

        Note: The architect's proposal has already been added to cur_messages by base_coder.py
        before this method is called. We analyze the proposal and, if appropriate, coordinate
        with editor and reviewer coders to implement and validate the changes.
        """
        architect_response = self.partial_response_content

        architect_response_codes = analyze_assistant_response(
            possible_architect_responses,
            (
                "Which one of the following choices best characterizes the assistant"
                " response shown below?"
            ),
            self.main_model.name,
            architect_response,
        )

        if architect_response_codes.has(
            architect_proposed_plan_changes
        ) or architect_response_codes.has(architect_proposed_non_plan_changes):
            exchange = ArchitectExchange(architect_response)
            self.process_architect_change_proposal(
                exchange, architect_response_codes.has(architect_proposed_plan_changes)
            )

    def process_architect_change_proposal(
        self, exchange: ArchitectExchange, is_plan_change: bool
    ) -> None:
        """Handle when architect proposes changes.

        Args:
            exchange: The exchange containing the architect's proposed changes

        The method coordinates the flow that occurs after the architect proposes changes:
        1. Get user confirmation to proceed with edits
        2. Execute changes via editor coder
        3. Review changes via reviewer coder
        4. Record the complete exchange
        """
        if not self.io.confirm_ask(
            'Should I edit files now? (Respond "No" to continue the conversation instead.)'
        ):
            return

        self.execute_changes(exchange, is_plan_change)
        # Only review if editing succeeded. A KeyboardInterrupt or model failure might
        # yield an empty response.
        if exchange.has_editor_response():
            self.review_changes(exchange)
        self.record_exchange(exchange)

    def execute_changes(self, exchange: ArchitectExchange, is_plan_change: bool) -> None:
        """Run the editor coder to implement changes.

        Args:
            exchange: The exchange containing the architect's proposed changes
        """
        editor_model = self.main_model.editor_model or self.main_model
        editor_coder = self.create_coder(
            edit_format=self.main_model.editor_edit_format,
            main_model=editor_model,
        )
        # Instead of mutating cur_messages, create new extended copy
        editor_coder.cur_messages = editor_coder.cur_messages + exchange.get_messages()

        if self.verbose:
            editor_coder.show_announcements()

        editor_prompt = exchange.append_editor_prompt(is_plan_change)
        editor_coder.run(with_message=editor_prompt, preproc=False)
        self.total_cost += editor_coder.total_cost
        self.aider_commit_hashes = editor_coder.aider_commit_hashes
        exchange.append_editor_response(editor_coder.partial_response_content)

    def review_changes(self, exchange: ArchitectExchange) -> None:
        """Run the reviewer coder to validate changes.

        Args:
            exchange: The exchange containing the architect and editor responses
        """
        self.io.tool_output("\nLooking over my changes ...")
        reviewer_coder = self.create_coder("ask")
        # Instead of mutating cur_messages, create new extended copy
        reviewer_coder.cur_messages = reviewer_coder.cur_messages + exchange.get_messages()
        reviewer_prompt = exchange.append_reviewer_prompt()
        reviewer_coder.run(with_message=reviewer_prompt, preproc=False)
        self.total_cost += reviewer_coder.total_cost
        exchange.append_reviewer_response(reviewer_coder.partial_response_content)

    def record_exchange(self, exchange: ArchitectExchange) -> None:
        """Record the complete conversation history.

        Args:
            exchange: The completed exchange containing all responses
        """
        self.cur_messages = self.cur_messages + exchange.get_messages()
        self.move_back_cur_messages(CHANGES_COMMITTED_MESSAGE)
        self.partial_response_content = ""  # Clear to prevent redundant message
