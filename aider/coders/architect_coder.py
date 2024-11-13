# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

from typing import Any, Optional

from ..sendchat import analyze_assistant_response
from .architect_prompts import (
    ArchitectPrompts,
    architect_asked_to_see_files,
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
    participant and to record the final conversation.
    
    Attributes:
        architect_response: The architect's response proposing changes
        editor_response: The editor's response after implementing changes
        reviewer_response: The reviewer's response after validating changes
    """

    # Standard user prompts used in the exchange
    APPROVE_CHANGES_PROMPT = "Yes, please make those changes."
    REVIEW_CHANGES_PROMPT = (
        "Please review the latest versions of the projects files that you just\n"
        "changed, focusing on your changes but considering other major issues\n"
        "also. If you have any substantial concerns, explain them and ask your\n"
        "partner if they'd like you to fix them. If you are satisfied with your\n"
        "changes, just briefly tell your partner that you reviewed them and\n"
        "believe they are fine."
    )
    CHANGES_COMMITTED_MESSAGE = (
        "The Brade application made those changes in the project files and committed them."
    )

    def __init__(self, architect_response: str):
        """Initialize a new exchange.
        
        Args:
            architect_response: The architect's response proposing changes
        """
        self.architect_response = architect_response
        self.editor_response: Optional[str] = None
        self.reviewer_response: Optional[str] = None

    def get_editor_messages(self) -> list[dict[str, str]]:
        """Get messages needed by editor to implement changes.
        
        Returns:
            List of messages for the editor's context
        """
        return [
            {"role": "assistant", "content": self.architect_response}
        ]

    def get_reviewer_messages(self) -> list[dict[str, str]]:
        """Get messages needed by reviewer to validate changes.
        
        Returns:
            List of messages for the reviewer's context
        """
        if not self.editor_response:
            raise ValueError("Editor response not yet set")
            
        return [
            {"role": "assistant", "content": self.architect_response},
            {"role": "user", "content": self.APPROVE_CHANGES_PROMPT},
            {"role": "assistant", "content": self.editor_response},
        ]

    def get_conversation_messages(self) -> list[dict[str, str]]:
        """Get the complete conversation record.
        
        Returns:
            List of all messages in the exchange
        """
        if not self.editor_response or not self.reviewer_response:
            raise ValueError("Exchange not complete")
            
        return [
            {"role": "assistant", "content": self.architect_response},
            {"role": "user", "content": self.APPROVE_CHANGES_PROMPT},
            {"role": "assistant", "content": self.editor_response},
            {"role": "user", "content": "Please review the changes that were just made. If you have any concerns, explain them."},
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

    edit_format = "architect"
    produces_code_edits = False  # Architect coder doesn't produce code edits directly
    gpt_prompts = ArchitectPrompts()

    def create_coder(self, coder_class: type[Coder], **kwargs: Any) -> Coder:
        """Creates a new coder instance with common setup.
        
        Args:
            coder_class: The coder class to instantiate
            **kwargs: Additional keyword arguments to pass to the coder constructor
            
        Returns:
            A configured coder instance ready for use
        """
        base_kwargs = dict(
            io=self.io,
            from_coder=self,
            suggest_shell_commands=False,
            map_tokens=0,
            total_cost=self.total_cost,
            cache_prompts=False,
            num_cache_warming_pings=0,
            summarize_from_coder=False,
        )
        base_kwargs.update(kwargs)
        
        coder = coder_class(self.main_model, **base_kwargs)
        coder.done_messages = list(self.done_messages)
        coder.cur_messages = list(self.cur_messages)
        return coder

    def handle_file_request(self, architect_response_codes: Any) -> None:
        """Handle when architect asks for files.
        
        Args:
            architect_response_codes: The analyzed response codes from the architect
        """
        if architect_response_codes.has(architect_asked_to_see_files):
            # Surrounding code will notice the paths and implement that.
            # If the architect responded with some blend of this choice and asking to edit
            # files, give it the additional files first and let it decide where to go from
            # there.
            pass

    def handle_proposed_changes(self, exchange: ArchitectExchange) -> None:
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
        self.record_conversation(exchange)

    def execute_changes(self, exchange: ArchitectExchange) -> None:
        """Run the editor coder to implement changes.
        
        Args:
            exchange: The exchange containing the architect's proposed changes
            
        Returns:
            The editor's response after implementing changes
        """
        editor_model = self.main_model.editor_model or self.main_model
        editor_coder = self.create_coder(
            Coder,
            main_model=editor_model,
            edit_format=self.main_model.editor_edit_format,
        )
        editor_coder.cur_messages.extend(exchange.get_editor_messages())

        if self.verbose:
            editor_coder.show_announcements()

        editor_coder.run(with_message=exchange.APPROVE_CHANGES_PROMPT, preproc=False)
        self.aider_commit_hashes = editor_coder.aider_commit_hashes
        exchange.editor_response = editor_coder.partial_response_content

    def review_changes(self, exchange: ArchitectExchange) -> None:
        """Run the reviewer coder to validate changes.
        
        Args:
            exchange: The exchange containing the architect and editor responses
            
        Returns:
            The reviewer's response after validating changes
        """
        reviewer_coder = self.create_coder(AskCoder)
        reviewer_coder.cur_messages.extend(exchange.get_reviewer_messages())
        reviewer_coder.run(with_message=exchange.REVIEW_CHANGES_PROMPT, preproc=False)
        self.total_cost = reviewer_coder.total_cost
        exchange.reviewer_response = reviewer_coder.partial_response_content

    def record_conversation(self, exchange: ArchitectExchange) -> None:
        """Record the complete conversation history.
        
        Args:
            exchange: The completed exchange containing all responses
        """
        self.cur_messages.extend(exchange.get_conversation_messages())
        self.move_back_cur_messages(exchange.CHANGES_COMMITTED_MESSAGE)
        self.partial_response_content = ""  # Clear to prevent redundant message

    def reply_completed(self) -> None:
        """Process the architect's response and coordinate with editor/reviewer as needed."""
        architect_response = self.partial_response_content

        # Analyze just the assistant's response
        architect_response_codes = analyze_assistant_response(
            possible_architect_responses,
            (
                "<SYSTEM> Which one of the following choices best characterizes the assistant"
                " response shown below?"
            ),
            self.main_model.name,
            architect_response,
        )

        # Handle different response types
        self.handle_file_request(architect_response_codes)
        
        if architect_response_codes.has(architect_proposed_changes):
            exchange = ArchitectExchange(architect_response)
            self.handle_proposed_changes(exchange)

        # Otherwise just let the conversation continue
