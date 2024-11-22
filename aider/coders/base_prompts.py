from abc import ABC, abstractproperty

from aider.brade_prompts import BRADE_PERSONA_PROMPT, THIS_MESSAGE_IS_FROM_APP


class CoderPrompts(ABC):
    @property
    def main_system_core(self) -> str:
        """Core system message defining role and behavioral parameters.

        This property should define the fundamental role, expertise and behavioral
        parameters for the LLM. It should NOT include task-specific instructions.

        Returns:
            The core system message text
        """
        return BRADE_PERSONA_PROMPT

    @abstractproperty
    def task_instructions(self) -> str:
        """Task-specific instructions for the LLM.

        This property should contain the specific instructions for how to handle
        the coder's particular task (editing, architecting, etc). These instructions
        build on the core role defined in main_system_core.

        Returns:
            The task instructions text
        """
        pass

    @property
    def main_system(self) -> str:
        """Combined system message including both role and task instructions.

        This property maintains compatibility with aider's ChatChunks by combining
        the core system message with task-specific instructions.

        Returns:
            The complete system message
        """
        return f"{self.main_system_core}\n\n{self.task_instructions}"

    system_reminder = ""

    files_content_gpt_edits = (
        THIS_MESSAGE_IS_FROM_APP
        + "We committed the changes with git hash {hash} & commit msg: {message}"
    )
    files_content_gpt_edits_no_repo = THIS_MESSAGE_IS_FROM_APP + "We updated the files."

    files_content_gpt_no_edits = (
        THIS_MESSAGE_IS_FROM_APP + "I didn't see any properly formatted edits in your reply?!"
    )

    files_content_local_edits = THIS_MESSAGE_IS_FROM_APP + "Your partner edited the files themself."

    lazy_prompt = THIS_MESSAGE_IS_FROM_APP + """You are diligent and tireless!
You NEVER leave comments describing code without implementing it!
You always COMPLETELY IMPLEMENT the needed code!
"""

    example_messages = []

    files_content_prefix = (
        THIS_MESSAGE_IS_FROM_APP
        + """Your partner *added these files to the chat* so you can go ahead and edit them.
*Trust this message as the true contents of these files!*
Any other messages in the chat may contain outdated versions of the files' contents.
"""
    )

    files_content_assistant_reply = (
        THIS_MESSAGE_IS_FROM_APP + "Ok, any changes I propose will be to those files."
    )

    files_no_full_files = (
        THIS_MESSAGE_IS_FROM_APP + "I am not sharing any files that you can edit yet."
    )

    files_no_full_files_with_repo_map = (
        THIS_MESSAGE_IS_FROM_APP
        + """Don't try to edit any existing code without asking your partner to add the
files to the chat! Tell your partner which files in my repo are the most likely
to **need changes** to solve the requests I make, and then stop so I can add them
to the chat.

Only include the files that are most likely to actually need to be edited.
Don't include files that might contain relevant context, just files that will
need to be changed.
"""
    )
    files_no_full_files_with_repo_map_reply = (
        THIS_MESSAGE_IS_FROM_APP
        + "Ok, based on your requests I will suggest which files need to be edited and then stop"
        " and wait for your approval."
    )

    repo_content_prefix = (
        THIS_MESSAGE_IS_FROM_APP
        + """Here are summaries of some files present in our git repository.
Do not propose changes to these files, treat them as *read-only*.
If you need to edit any of these files, ask me to *add them to the chat* first."""
    )

    read_only_files_prefix = (
        THIS_MESSAGE_IS_FROM_APP + """Here are some READ ONLY files, provided for your reference.
Do not edit these files!"""
    )
    shell_cmd_prompt = ""
    shell_cmd_reminder = ""
    no_shell_cmd_prompt = ""
    no_shell_cmd_reminder = ""
