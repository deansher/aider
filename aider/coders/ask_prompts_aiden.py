# flake8: noqa: E501

from . import aiden_prompts
from .base_prompts import CoderPrompts


class AskPrompts(CoderPrompts):
    code_analyst = """Act as an expert code analyst.
Answer questions about the supplied code.
"""

    main_system = (
        aiden_prompts.aiden_persona_intro + aiden_prompts.system_information + code_analyst
    )

    example_messages = []

    files_content_prefix = """I have *added these files to the chat* so you see all of their contents.
*Trust this message as the true contents of the files!*
Other messages in the chat may contain outdated versions of the files' contents.
"""  # noqa: E501

    files_no_full_files = "I am not sharing the full contents of any files with you yet."

    files_no_full_files_with_repo_map = ""
    files_no_full_files_with_repo_map_reply = ""

    repo_content_prefix = """I am working with you on code in a git repository.
Here are summaries of some files present in my git repo.
If you need to see the full contents of any files to answer my questions, ask me to *add them to the chat*.
"""

    system_reminder = ""
