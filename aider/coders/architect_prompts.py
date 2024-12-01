# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

# flake8: noqa: E501

from llm_multiple_choice import ChoiceManager

from aider.brade_prompts import CONTEXT_NOUN, THIS_MESSAGE_IS_FROM_APP

from .base_prompts import CoderPrompts

# Message constants used in architect exchanges
APPROVED_CHANGES_PROMPT: str = "Yes, please make those changes."

REVIEW_CHANGES_PROMPT: str = f"""{THIS_MESSAGE_IS_FROM_APP}
Review the latest versions of the project files that you just changed.
Study the latest versions of these files, which are provided in {CONTEXT_NOUN}.
Read with a fresh, skeptical eye. 

Preface your response with the markdown header "# Reasoning". Then think out loud, 
step by step, as you review the affected portions of the modified files. 
Think about whether the updates fully and correctly achieve
the goals for this work. Think about whether any new problems were introduced,
and whether any serious existing problems in the affected content were left unaddressed.

When you are finished thinking through the changes, mark your transition to
your conclusions with a "# Conclusions" markdown header. Then, concisely explain
what you believe about the changes.

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

CHANGES_COMMITTED_MESSAGE: str = (
    THIS_MESSAGE_IS_FROM_APP
    + "The Brade application made those changes in the project files and committed them."
)

ARCHITECT_RESPONSE_CHOICES: str = """
At each point in the conversation, first decide whether to respond immediately or
take time to think.

- You should respond immediately if you are very confident that you can give a simple,
  direct, and correct response based on things you already know.

- But if you are at all unsure whether your immediate answer would be correct, then you 
  should take time to think.

# Taking Time to Think

If you choose to take time to think, begin your response with a markdown header "# Reasoning".
Then think out loud, step by step, until you are confident you know the right answer.

# Ways you Can Respond

Regardless of whether you took time to think, you can choose to respond in any of the following 
three ways. If you did take time to think, then use the indicated section heading for your
response. Otherwise, omit the section heading and simply jump into your response.

You can choose to just **respond conversationally** as part of your ongoing collaboration. 
(If you took time to think, use a "# Response" heading to mark the transition from your reasoning
to your response.)

Alternatively, you have two ways to respond that will cause the Brade application to take
specific actions:

- You can **propose changes** that you would make as a next step. (If you took time to think,
  use a "# Proposal" heading to mark this transition.)

  In this case, clearly state that you propose to edit project files. If it's not obvious from the
  discussion, explain your goals. In any case, briefly think aloud through any especially important 
  or difficult decisions or issues. Next, write clear, focused instructions for the changes. 
  Make these concrete enough to act on, but brief enough to easily review. Don't propose specific
  new code or propose at this stage. Conclude your response by asking your partner whether you 
  should make the changes you proposed.

  If you respond in this manner, the Brade application will ask your partner whether they want 
  you to go ahead and make file changes, (Y)es or (n)o. If they answer "yes", the Brade 
  application will walk you through a process for making the changes. This is how you do work
  on the project.

  Special note for plan documents: If asked to update a plan, don't write the plan content yet. 
  Instead, briefly indicate the kinds of plan updates you propose to make and ask whether to 
  proceed.

- Or, you can ask to see more files. (If you took time to think, mark this transition with a
  "# Request for Files" heading.) Provide the files' paths relative to the project root and and 
  explain why you need them. In this case, the Brade application will ask your partner whether
  it is ok to provide those files to you.
"""

# Define the choice manager for analyzing architect responses
possible_architect_responses: ChoiceManager = ChoiceManager()


# Preface each line of ARCHITECT_RESPONSE_CHOICES with "> " to quote it.
quoted_response_choices: str = "> " + "\n> ".join(ARCHITECT_RESPONSE_CHOICES.split("\n")) + "\n"


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
    """Prompts and configuration for the architect workflow.
    
    This class extends CoderPrompts to provide specialized prompts and configuration
    for the architect workflow, which focuses on collaborative software development
    with a human partner.
    """

    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the architect workflow.
        
        Returns:
            Instructions for collaborating naturally with a human partner to make
            steady project progress through small, focused steps.
        """
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

    architect_response_analysis_prompt: tuple = ()

    example_messages: list = []

    files_content_prefix: str = ""

    files_content_assistant_reply: str = (
        "Ok, I will use that as the true, current contents of the files."
    )

    files_no_full_files: str = (
        THIS_MESSAGE_IS_FROM_APP
        + "Your partner has not shared the full contents of any files with you yet."
    )

    files_no_full_files_with_repo_map: str = ""
    files_no_full_files_with_repo_map_reply: str = ""

    repo_content_prefix: str = ""

    system_reminder: str = ""

    editor_response_placeholder: str = (
        THIS_MESSAGE_IS_FROM_APP
        + """An editor AI persona has followed your instructions to make changes to the project
        files. They probably made changes, but they may have responded in some other way.
        Your partner saw the editor's output, including any file changes, in the Brade application
        as it was generated. Any changes have been saved to the project files and committed
        into our git repo. You can see the updated project information in the <context> provided 
        for you in your partner's next message.
"""
    )
