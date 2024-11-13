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

    def handle_proposed_changes(self, architect_response: str) -> None:
        """Handle when architect proposes changes.
        
        Args:
            architect_response: The architect's response proposing changes
        """
        if not self.io.confirm_ask(
            'Should I edit files now? (Respond "No" to continue the conversation instead.)'
        ):
            return

        editor_response = self.execute_changes(architect_response)
        reviewer_response = self.review_changes(architect_response, editor_response)
        self.record_conversation(architect_response, editor_response, reviewer_response)

    def execute_changes(self, architect_response: str) -> str:
        """Run the editor coder to implement changes.
        
        Args:
            architect_response: The architect's response containing proposed changes
            
        Returns:
            The editor's response after implementing changes
        """
        editor_model = self.main_model.editor_model or self.main_model
        editor_coder = self.create_coder(
            Coder,
            main_model=editor_model,
            edit_format=self.main_model.editor_edit_format,
        )
        editor_coder.cur_messages.append(
            {"role": "assistant", "content": architect_response}
        )

        if self.verbose:
            editor_coder.show_announcements()

        editor_coder.run(with_message="Yes, please make those changes.", preproc=False)
        self.aider_commit_hashes = editor_coder.aider_commit_hashes
        return editor_coder.partial_response_content

    def review_changes(self, architect_response: str, editor_response: str) -> str:
        """Run the reviewer coder to validate changes.
        
        Args:
            architect_response: The architect's response containing proposed changes
            editor_response: The editor's response after implementing changes
            
        Returns:
            The reviewer's response after validating changes
        """
        reviewer_coder = self.create_coder(AskCoder)
        reviewer_coder.cur_messages.extend([
            {"role": "assistant", "content": architect_response},
            {"role": "user", "content": "Yes, please make those changes."},
            {"role": "assistant", "content": editor_response},
        ])

        reviewer_coder.run(
            with_message=(
                "Please review the latest versions of the projects files that you just\n"
                "changed, focusing on your changes but considering other major issues\n"
                "also. If you have any substantial concerns, explain them and ask your\n"
                "partner if they'd like you to fix them. If you are satisfied with your\n"
                "changes, just briefly tell your partner that you reviewed them and\n"
                "believe they are fine."
            ),
            preproc=False,
        )
        self.total_cost = reviewer_coder.total_cost
        return reviewer_coder.partial_response_content

    def record_conversation(
        self, 
        architect_response: str, 
        editor_response: str, 
        reviewer_response: str
    ) -> None:
        """Record the complete conversation history.
        
        Args:
            architect_response: The architect's response containing proposed changes
            editor_response: The editor's response after implementing changes
            reviewer_response: The reviewer's response after validating changes
        """
        self.cur_messages.extend([
            {"role": "assistant", "content": architect_response},
            {"role": "user", "content": "Yes, please make those changes."},
            {"role": "assistant", "content": editor_response},
            {"role": "user", "content": "Please review the changes that were just made. If you have any concerns, explain them."},
            {"role": "assistant", "content": reviewer_response},
        ])

        self.move_back_cur_messages(
            "The Brade application made those changes in the project files and committed"
            " them."
        )
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
            self.handle_proposed_changes(architect_response)

        # Otherwise just let the conversation continue
