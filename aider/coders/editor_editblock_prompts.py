# flake8: noqa: E501

from .editblock_prompts import EditBlockPrompts


class EditorEditBlockPrompts(EditBlockPrompts):
    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the edit block workflow."""
        return """
Describe each change with a *SEARCH/REPLACE block* per the examples below.
All changes to files must use this *SEARCH/REPLACE block* format.
ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!
"""

    shell_cmd_prompt = ""
    no_shell_cmd_prompt = ""
    shell_cmd_reminder = ""
