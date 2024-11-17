# flake8: noqa: E501

from llm_multiple_choice import ChoiceManager

from aider.coders.format_brade_messages import THIS_MESSAGE_IS_FROM_APP

from .base_prompts import CoderPrompts

# Message constants used in architect exchanges
APPROVED_CHANGES_PROMPT = "Yes, please make those changes."
REVIEW_CHANGES_PROMPT = (
    THIS_MESSAGE_IS_FROM_APP
    + "Please review the latest versions of the projects files that you just\n"
    "changed, focusing on your changes but considering other major issues\n"
    "also. If you have any substantial concerns, explain them and ask your\n"
    "partner if they'd like you to fix them. If you are satisfied with your\n"
    "changes, just briefly tell your partner that you reviewed them and\n"
    "believe they are fine."
)
CHANGES_COMMITTED_MESSAGE = (
    THIS_MESSAGE_IS_FROM_APP
    + "The Brade application made those changes in the project files and committed them."
)

# Define the choice manager for analyzing architect responses
possible_architect_responses = ChoiceManager()
response_section = possible_architect_responses.add_section(
    "Analyze the assistant's response. Choose the single most appropriate option.",
)
architect_asked_to_see_files = response_section.add_choice(
    "The architect asked to see additional files."
)
architect_proposed_changes = response_section.add_choice(
    "The architect explained how it would create or modify code or "
    "other content and asked if it should proceed accordingly."
)
architect_continued_conversation = response_section.add_choice(
    "None of the above. The architect just continued the conversation, such as by "
    "answering a question, asking questions, or making a suggestion that "
    "stops short of proposing specific work."
)


class ArchitectPrompts(CoderPrompts):
    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the architect workflow."""
        return """
Your goal is to help your partner make steady progress through a series of small, focused steps. Start by proposing a concrete next step that moves the project forward.

If your partner's request is specific, follow it precisely. If it's more open-ended, look for the simplest change that would make things better. Lead your response by proposing this concrete step so your partner can quickly evaluate if it's what they want.

You have three ways to respond:

1. Propose specific changes to make. Start with "Here is how I would" and briefly state your goal. Then think through any tricky issues. Write clear, focused instructions for the changes - concrete enough to act on, but brief enough to easily review. Don't include actual content yet. Finally, summarize the key points so your partner can quickly decide whether to proceed.

2. Ask to see more files that you need, with their full paths and why you need them.

3. Continue the conversation by answering questions, asking questions, or making suggestions that need more discussion before proposing specific changes.

For any response type, stop after making your proposal and wait for your partner's input.

Special note for plan documents: If asked to update a plan, don't write the plan content yet. Instead, briefly confirm what updates are needed and ask to proceed.

After your partner responds, you'll take the appropriate next action.
"""

    example_messages = []

    files_content_prefix = ""

    files_content_assistant_reply = (
        "Ok, I will use that as the true, current contents of the files."
    )

    files_no_full_files = (
        THIS_MESSAGE_IS_FROM_APP
        + "Your partner has not shared the full contents of any files with you yet."
    )

    files_no_full_files_with_repo_map = ""
    files_no_full_files_with_repo_map_reply = ""

    repo_content_prefix = ""

    system_reminder = ""

    editor_response_placeholder = (
        THIS_MESSAGE_IS_FROM_APP
        + """An editor AI persona has followed your instructions to make changes to the project
        files. They probably made changes, but they may have responded in some other way.
        Your partner saw the editor's output, including any file changes, in the Brade application
        as it was generated. Any changes have been saved to the project files and committed
        into our git repo. You can see the updated project information in the <context> provided 
        for you in your partner's next message.
"""
    )
