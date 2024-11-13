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
    edit_format = "architect"
    produces_code_edits = False  # Architect coder doesn't produce code edits directly
    gpt_prompts = ArchitectPrompts()

    def reply_completed(self):
        architect_response = self.partial_response_content

        # Analyze just the assistant's response
        architect_response_codes = analyze_assistant_response(
            possible_architect_responses,
            (
                "Which one of the following choices best characterizes the assistant"
                " response shown below?"
            ),
            self.main_model.name,
            architect_response,
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
                editor_coder.done_messages = list(self.done_messages)
                editor_coder.cur_messages = list(self.cur_messages)
                editor_coder.cur_messages.append(
                    {
                        "role": "assistant",
                        "content": architect_response,
                    }
                )

                if self.verbose:
                    editor_coder.show_announcements()

                editor_coder.run(with_message="Yes, please make those changes.", preproc=False)

                # Create an AskCoder instance to review the changes
                reviewer_coder = AskCoder(
                    self.main_model,
                    self.io,
                    from_coder=self,
                    suggest_shell_commands=False,
                    map_tokens=0,
                    total_cost=editor_coder.total_cost,
                    cache_prompts=False,
                    num_cache_warming_pings=0,
                    summarize_from_coder=False,
                )
                reviewer_coder.done_messages = list(self.done_messages)
                reviewer_coder.cur_messages = list(self.cur_messages)
                reviewer_coder.cur_messages.extend(
                    [
                        {"role": "assistant", "content": architect_response},
                        {"role": "user", "content": "Yes, please make those changes."},
                    ]
                )

                # Have AskCoder review the changes
                reviewer_coder.run(
                    with_message="Please review the changes that were just made. If you have any concerns, explain them.",
                    preproc=False,
                )
                reviewer_response = reviewer_coder.partial_response_content

                # Record the entire conversation including all responses
                self.cur_messages.extend(
                    [
                        {"role": "assistant", "content": architect_response},
                        {"role": "user", "content": "Yes, please make those changes."},
                        {"role": "assistant", "content": editor_response},
                        {"role": "user", "content": "Please review the changes that were just made. If you have any concerns, explain them."},
                        {"role": "assistant", "content": reviewer_response},
                    ]
                )
                self.move_back_cur_messages(self.gpt_prompts.editor_response_placeholder)
                self.partial_response_content = ""  # Clear to prevent redundant message
                self.total_cost += editor_coder.total_cost + reviewer_coder.total_cost
                self.aider_commit_hashes = editor_coder.aider_commit_hashes

        # Otherwise just let the conversation continue
