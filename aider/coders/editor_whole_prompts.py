# flake8: noqa: E501

from .wholefile_prompts import WholeFilePrompts


class EditorWholeFilePrompts(WholeFilePrompts):
    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for editor mode."""
        return """
{lazy_prompt}
Output a copy of each file that needs changes.
"""
