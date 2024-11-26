# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

from typing import Any, Optional

from ..sendchat import analyze_assistant_response
from .architect_prompts import (
    APPROVED_CHANGES_PROMPT,
    CHANGES_COMMITTED_MESSAGE,
    REVIEW_CHANGES_PROMPT,
    ArchitectPrompts,
    architect_proposed_changes,
    possible_architect_responses,
)
from .ask_coder import AskCoder
from .base_coder import Coder


class ArchitectExchange:
    """Encapsulates a complete architect-editor-reviewer exchange.

    This class manages the messages and responses for a complete exchange between:
    - The architect proposing changes
    - The editor implementing changes
    - The reviewer validating changes

    It provides methods to generate the appropriate message sequences needed by each
    participant and for recording the entire exchange.

    Attributes:
        architect_response: The architect's response proposing changes
        editor_response: The editor's response after implementing changes
        reviewer_response: The reviewer's response after validating changes
    """

    def __init__(self, architect_response: str):
        """Initialize a new exchange.

        Args:
            architect_response: The architect's response proposing changes
        """
        self.architect_response = architect_response
        self.editor_response: Optional[str] = None
        self.reviewer_response: Optional[str] = None

    def _architect_message(self) -> dict[str, str]:
        """Get the architect's proposal message.

        Returns:
            The architect's message proposing changes
        """
        return {"role": "assistant", "content": self.architect_response}

    def _architect_editor_exchange(self) -> list[dict[str, str]]:
        """Get the architect-editor exchange messages.

        Returns:
            List of messages for the architect-editor exchange

        Raises:
            ValueError: If editor response is not yet set
        """
        if not self.editor_response:
            raise ValueError("Editor response not yet set")

        return [
            self._architect_message(),
            {"role": "user", "content": APPROVED_CHANGES_PROMPT},
            {"role": "assistant", "content": self.editor_response},
        ]

    def get_editor_messages(self) -> list[dict[str, str]]:
        """Get messages needed by editor to implement changes.

        Returns:
            List of messages for the editor's context
        """
        return [self._architect_message()]

    def get_reviewer_messages(self) -> list[dict[str, str]]:
        """Get messages needed by reviewer to validate changes.

        Returns:
            List of messages for the reviewer's context
        """
        return self._architect_editor_exchange()

    def get_entire_exchange(self) -> list[dict[str, str]]:
        """Get the complete conversation record, after the architect, editor, and reviewer
        have all participated.

        Returns:
            List of all messages in the exchange

        Raises:
            ValueError: If exchange is not complete
        """
        if not self.editor_response or not self.reviewer_response:
            raise ValueError("Exchange not complete")

        return self._architect_editor_exchange() + [
            {"role": "user", "content": REVIEW_CHANGES_PROMPT},
            {"role": "assistant", "content": self.reviewer_response},
        ]


class ArchitectCoder(AskCoder):
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
        """Process the architect's response and coordinate with editor/reviewer as needed."""
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

        if architect_response_codes.has(architect_proposed_changes):
            exchange = ArchitectExchange(architect_response)
            self.process_architect_change_proposal(exchange)

    def process_architect_change_proposal(self, exchange: ArchitectExchange) -> None:
        """Handle when architect proposes changes.

        Args:
            exchange: The exchange containing the architect's proposed changes
        """
        if not self.io.confirm_ask(
            'Should I edit files now? (Respond "No" to continue the conversation instead.)'
        ):
            return

        self.execute_changes(exchange)
        self.review_changes(exchange)
        self.record_entire_exchange(exchange)

    def execute_changes(self, exchange: ArchitectExchange) -> None:
        """Run the editor coder to implement changes.

        Args:
            exchange: The exchange containing the architect's proposed changes

        Returns:
            The editor's response after implementing changes
        """
        editor_model = self.main_model.editor_model or self.main_model
        editor_coder = self.create_coder(
            edit_format=self.main_model.editor_edit_format,
            main_model=editor_model,
        )
        # Instead of mutating cur_messages, create new extended copy
        editor_coder.cur_messages = editor_coder.cur_messages + exchange.get_editor_messages()

        if self.verbose:
            editor_coder.show_announcements()

        editor_coder.run(with_message=APPROVED_CHANGES_PROMPT, preproc=False)
        self.total_cost += editor_coder.total_cost
        self.aider_commit_hashes = editor_coder.aider_commit_hashes
        exchange.editor_response = editor_coder.partial_response_content

    def review_changes(self, exchange: ArchitectExchange) -> None:
        """Run the reviewer coder to validate changes.

        Args:
            exchange: The exchange containing the architect and editor responses

        Returns:
            The reviewer's response after validating changes
        """
        self.io.tool_output("\nLooking over my changes ...")
        reviewer_coder = self.create_coder("ask")
        # Instead of mutating cur_messages, create new extended copy
        reviewer_coder.cur_messages = reviewer_coder.cur_messages + exchange.get_reviewer_messages()
        reviewer_coder.run(with_message=REVIEW_CHANGES_PROMPT, preproc=False)
        self.total_cost += reviewer_coder.total_cost
        exchange.reviewer_response = reviewer_coder.partial_response_content

    def record_entire_exchange(self, exchange: ArchitectExchange) -> None:
        """Record the complete conversation history.

        Args:
            exchange: The completed exchange containing all responses
        """
        self.cur_messages = self.cur_messages + exchange.get_entire_exchange()
        self.move_back_cur_messages(CHANGES_COMMITTED_MESSAGE)
        self.partial_response_content = ""  # Clear to prevent redundant message
