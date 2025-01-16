# flake8: noqa: E501

"""Prompts for the editor coder that implements changes using SEARCH/REPLACE blocks.

This class configures the prompts that the editor coder receives. The prompts come from
multiple sources and are assembled into a sequence of chat messages:

1. System Message:
   a. Core persona (from CoderPrompts.main_system_core):
      - General Brade persona and collaboration approach
      - Included at start of system message

   b. Context (from Coder._format_brade_messages):
      - Repository map and file contents
      - Appended to system message

   c. Task Instructions (from this class):
      - Brief instruction to make changes using SEARCH/REPLACE blocks
      - Reference to examples
      - Appended to system message

   d. Task Examples (from EditBlockPrompts):
      - Example SEARCH/REPLACE blocks showing format
      - Appended to system message

2. Previous Messages (from architect coder):
   - Architect's chat history
   - Architect's proposal for current change

3. Final User Message:
   a. System Reminder (from EditBlockPrompts):
      - Detailed requirements for SEARCH/REPLACE blocks
      - Format specifications and examples
      - Common mistakes to avoid
      - Special cases
      - Prepended to final user message

   b. Editor Prompt (from ArchitectPrompts):
      - Instructions for current implementation task
      - Appended to final user message

The editor coder's job is to implement changes that have already been approved. It does
not participate in high-level decision making or the three-step process. It focuses solely
on implementing changes correctly using SEARCH/REPLACE blocks.
"""

from .editblock_prompts import EditBlockPrompts


class EditorEditBlockPrompts(EditBlockPrompts):
    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the edit block workflow."""
        return """
 You are implementing changes that you proposed and your partner approved. Your job is to:
 - Make exactly the changes outlined in your proposal
 - Use SEARCH/REPLACE blocks to specify each change
 - Follow the format requirements precisely
 - Focus solely on implementation
 - Stop when done so you can review the changes

 After you specify the changes and stop, the Brade application will apply them to the
 project files. Then you will review the updated files to ensure the changes fully and
 correctly implement your proposal.

 Make each change by producing a *SEARCH/REPLACE block* as instructed below. You must use
 precisely this format. Study the <task_examples>...</task_examples> to ensure that you
 understand it.
 """

    shell_cmd_prompt = ""
    no_shell_cmd_prompt = ""
    shell_cmd_reminder = ""
