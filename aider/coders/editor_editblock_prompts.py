# flake8: noqa: E501

from .editblock_prompts import EditBlockPrompts


class EditorEditBlockPrompts(EditBlockPrompts):
    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the edit block workflow."""
        return """
Make file changes to implement the step that you and your partner have agreed you will take.
Make each change by producing a *SEARCH/REPLACE block* as instructed below. 
You must use precisely this format. Study the <task_examples>...</task_examples>
to ensure that you understand it.
"""

    shell_cmd_prompt = ""
    no_shell_cmd_prompt = ""
    shell_cmd_reminder = ""
