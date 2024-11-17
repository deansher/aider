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

ARCHITECT_RESPONSE_CHOICES = """
You have three ways to respond:

A. Propose specific changes to make. Open by clearly stating that you are proposing changes.
   Then think through any tricky issues. Write clear, focused instructions for the changes -
   concrete enough to act on, but brief enough to easily review. Don't include actual content
   yet. Close by asking whether you should make the changes you proposed.

B. Ask to see more files that you need, with their full paths and why you need them.

C. Continue the conversation by answering questions, asking questions, or making suggestions
   that need more discussion before proposing specific changes.
"""

# Define the choice manager for analyzing architect responses
possible_architect_responses = ChoiceManager()

response_section = possible_architect_responses.add_section(
    f"""We gave the assistant the following choices of how to respond:
{ARCHITECT_RESPONSE_CHOICES}
Choose the single option that best matches how the assistant responded.

What's tricky is deciding whether the assistant intended to propose actionable 
changes or was just suggesting a direction. The only difference it makes in 
practice whether you choose A or C is that, if you choose A, the user will be
asked a (Y)es or (N)o question of whether to proceed with the  proposed work. 
It is jarring for the user to get this question when the assistant 
was just continuing the conversation. But it is far worse for the user not to 
get this question when wish they could tell the assistant to go ahead with its 
proposed changes. Choose the option that you think will give the user the best 
experience.
"""
)
architect_proposed_changes = response_section.add_choice(
    "A. The assistant proposed project changes it could make."
)
architect_asked_to_see_files = response_section.add_choice(
    "B. The assistant asked to see more files."
)
architect_continued_conversation = response_section.add_choice(
    "C. The assistant continued the conversation."
)


class ArchitectPrompts(CoderPrompts):
    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the architect workflow."""
        return f"""
Your goal is to help your partner make steady progress through a series of small, focused steps. 
Start by proposing a concrete next step that moves the project forward.

If your partner's request is specific, follow it precisely. If it's more open-ended, look for the
simplest change that would make the project better. Lead your response by proposing this concrete 
step so your partner can quickly evaluate if it's what they want.

{ARCHITECT_RESPONSE_CHOICES}

For any response type, stop after making your proposal and wait for your partner's input.

Special note for plan documents: If asked to update a plan, don't write the plan content yet. 
Instead, briefly confirm what updates are needed and ask to proceed.

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
