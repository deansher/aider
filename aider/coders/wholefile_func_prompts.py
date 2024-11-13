# flake8: noqa: E501

from .base_prompts import CoderPrompts


class WholeFileFunctionPrompts(CoderPrompts):
    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for function-based editing workflow."""
        return """
Reply to your partner in the same language they are using.

Once you understand the request you MUST use the `write_file` function to edit the files to make the needed changes.
"""

    system_reminder = """
ONLY return code using the `write_file` function.
NEVER return code outside the `write_file` function.
"""

    files_content_prefix = "Here is the current content of the files:\n"
    files_no_full_files = "I am not sharing any files yet."

    redacted_edit_message = "No changes are needed."

    # TODO: should this be present for using this with gpt-4?
    repo_content_prefix = None

    # TODO: fix the chat history, except we can't keep the whole file
