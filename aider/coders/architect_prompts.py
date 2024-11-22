# flake8: noqa: E501

from llm_multiple_choice import ChoiceManager

from aider.brade_prompts import THIS_MESSAGE_IS_FROM_APP

from .base_prompts import CoderPrompts

# Message constants used in architect exchanges
APPROVED_CHANGES_PROMPT = "Yes, please make those changes."
REVIEW_CHANGES_PROMPT = f"""{THIS_MESSAGE_IS_FROM_APP}
Please review the latest versions of the projects files that you just
changed. Read your changes with a fresh skeptical eye, looking for problems you
might have introduced and for ways you fell short of your partner's instructions
and your own standards.

Use this ONLY as an opportunity to find and point out problems that are
significant enough -- at this stage of your work with your partner -- to take
time together to address them. If you believe you already did an excellent job
with your partner's request, just say you are fully satisfied with your changes
and stop there. If you see opportunities to improve but believe they are good
enough for now, give an extremely concise summary of opportunities to improve
(in a sentence or two), but also say you believe this could be fine for now.

If you see substantial problems in the changes you made, explain what you see
in some detail.

Don't point out other problems in these files unless they are immediately concerning.
Take into account the overall state of development of the code, and the cost
of interrupting the process that you and your partner are following together.
Your partner may clear the chat -- they may choose to do this frequently -- so
one cost of pointing out problems in other areas of the code is that you may do
so repeatedly without knowing it. All that said, if you see an immediately concerning
problem in parts of the code that you didn't just change, and if you believe it is
appropriate to say so to your partner, trust your judgment and do so.
"""
CHANGES_COMMITTED_MESSAGE = (
    THIS_MESSAGE_IS_FROM_APP
    + "The Brade application made those changes in the project files and committed them."
)

ARCHITECT_RESPONSE_CHOICES = """
At each point in the conversation, you can choose to just **respond conversationally** as 
part of your ongoing collaboration. 

Alternatively, you have two ways to respond that will cause the Brade application to take
specific actions:

- You can **propose changes** that you would make as a next step. In this case, 
  clearly state that you are proposing changes to project files. Then briefly think aloud through 
  any especially important or difficult decisions or issues in what you are about to propose. Next, write clear, 
  focused instructions for the changes. Make these concrete enough to act on, but brief enough 
  to easily review. Don't propose actual changes or file content at this stage. Conclude your 
  response by asking your partner whether you should make the changes you proposed.

  If you respond in this manner, the Brade application will ask your partner whether they want 
  you to go ahead and make file changes, (Y)es or (n)o. If they answer "yes", the Brade 
  application will walk you through a process for making the changes. This is how you do work
  on the project.

  Special note for plan documents: If asked to update a plan, don't write the plan content yet. 
  Instead, briefly confirm what plan updates are needed and ask whether to proceed.

- Or, you can **ask to see more files**. Provide their paths relative to the project root and and 
  explain why you need them. In this case, the Brade application will ask your partner whether
  it is ok to provide those files to you.
"""

# Define the choice manager for analyzing architect responses
possible_architect_responses = ChoiceManager()


# Preface each line of ARCHITECT_RESPONSE_CHOICES with "> " to quote it.
quoted_response_choices = "> " + "\n> ".join(ARCHITECT_RESPONSE_CHOICES.split("\n")) + "\n"


response_section = possible_architect_responses.add_section(
    f"""Compare the assistant's response to the choices we gave it for how to respond. 
Decide whether the assistant's human partner will be best served by having the Brade 
application take one of the special actions, or by simply treating the assistant's response 
as conversation. Do this by choosing the single best option from the list below.

Select the **proposed changes** option if you think there's a reasonable chance the
user would like to interpret the assistants's answer as a proposal to make changes,
and would like to be able to say "yes" to it. This gives the assistant's human partner 
an opportunity to make that decision for themself.  But if it is clear to you that the 
assistant has not proposed anything concrete enough to say "yes" to, then choose one of
the other options.

Here is the explanation we gave to the assistant on how it could choose to respond:

{quoted_response_choices}
"""
)
architect_proposed_changes = response_section.add_choice(
    "The assistant **proposed changes** that she could make."
)
architect_asked_to_see_files = response_section.add_choice(
    "The assistant **asked to see more files**."
)
architect_continued_conversation = response_section.add_choice(
    "The assistant **responded conversationally**."
)


class ArchitectPrompts(CoderPrompts):
    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the architect workflow."""
        return f"""Collaborate naturally with your partner. Together, seek ways to
make steady project progress through a series of small, focused steps. Try to do
as much of the work as you feel qualified to do well. Rely on your partner mainly
for review. If your partner wants you to do something that you don't feel you can
do well, explain your concerns and work with them on a more approachable next step.
Perhaps they need to define the task more clearly, give you a smaller task, do a 
piece of the work themselves, provide more context, or something else. Just be direct
and honest with them about your skills, understanding of the context, and high or
low confidence.

{ARCHITECT_RESPONSE_CHOICES}
"""

    architect_response_analysis_prompt = ()

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
