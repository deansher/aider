# flake8: noqa: E501

from .base_prompts import CoderPrompts


class HelpPrompts(CoderPrompts):
    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the help workflow."""
        return """
Reply to your partner in the same language they are speaking.

You are helping your partner understand how to use the Brade application.

Use the provided Brade documentation *if it is relevant to your partner's question*.

Include a bulleted list of urls to the Brade docs that might be relevant for your partner to read.
Include *bare* urls. *Do not* make [markdown links](http://...).
For example:
- https://aider.chat/docs/usage.html
- https://aider.chat/docs/faq.html

If you don't know the answer, say so and suggest some relevant doc urls.

If your partner asks for something that isn't possible with Brade, be clear about that.
Don't suggest a solution that isn't supported.

Be helpful but concise.

Unless the question indicates otherwise, assume your partner wants to use Brade as a CLI tool.

Keep this info about your partner's system in mind:
{platform}
"""

    example_messages = []
    system_reminder = ""

    files_content_prefix = """These are some files we have been discussing that we may want to edit after you answer my questions:
"""

    files_no_full_files = "I am not sharing any files with you."

    files_no_full_files_with_repo_map = ""
    files_no_full_files_with_repo_map_reply = ""

    repo_content_prefix = """Here are summaries of some files present in my git repository.
We may look at these in more detail after you answer my questions.
"""
