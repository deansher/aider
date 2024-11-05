from ..sendchat import analyze_chat_situation
from .architect_prompts import (
    ArchitectPrompts,
    architect_asked_to_see_files,
    architect_proposed_changes,
    possible_architect_responses,
)
from .ask_coder import AskCoder
from .base_coder import Coder


class ArchitectCoder(AskCoder):
    edit_format = "architect"
    produces_code_edits = False  # Architect coder doesn't produce code edits directly
    gpt_prompts = ArchitectPrompts()

    def reply_completed(self):
        assistant_response = self.partial_response_content

        # Create a list of messages that includes both the current conversation turn
        # and the latest response
        messages_to_analyze = list(self.cur_messages)  # Copy current messages
        messages_to_analyze.append({
            "role": "assistant",
            "content": assistant_response
        })

        # Use the complete set of messages in the analysis
        architect_response_codes = analyze_chat_situation(
            possible_architect_responses,
            (
                "<SYSTEM> Which one of the following choices best characterizes how the assistant"
                " replied above?"
            ),
            self.main_model.name,
            messages_to_analyze,  # Use the complete set of messages
        )

        # If architect asked for files, prompt user to add them
        if architect_response_codes.has(architect_asked_to_see_files):
            # Surrounding code will notice the paths and implement that.
            # If the architect responded with some blend of this choice and asking to edit
            # files, give it the additional files first and let it decide where to go from
            # there.
            pass

        # If architect proposed edits, confirm and proceed with editor
        elif architect_response_codes.has(architect_proposed_changes):
            if self.io.confirm_ask(
                'Should I edit files now? (Respond "No" to continue the conversation instead.)'
            ):
                kwargs = dict()
                editor_model = self.main_model.editor_model or self.main_model
                kwargs["main_model"] = editor_model
                kwargs["edit_format"] = self.main_model.editor_edit_format
                kwargs["suggest_shell_commands"] = False
                kwargs["map_tokens"] = 0
                kwargs["total_cost"] = self.total_cost
                kwargs["cache_prompts"] = False
                kwargs["num_cache_warming_pings"] = 0
                kwargs["summarize_from_coder"] = False

                new_kwargs = dict(io=self.io, from_coder=self)
                new_kwargs.update(kwargs)

                editor_coder = Coder.create(**new_kwargs)
                editor_coder.cur_messages = []
                editor_coder.done_messages = []

                if self.verbose:
                    editor_coder.show_announcements()

                editor_coder.run(with_message=assistant_response, preproc=False)

                self.move_back_cur_messages("I made those changes to the files.")
                self.total_cost = editor_coder.total_cost
                self.aider_commit_hashes = editor_coder.aider_commit_hashes

        # Otherwise just let the conversation continue
