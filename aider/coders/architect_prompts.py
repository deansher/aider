# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

# flake8: noqa: E501

from llm_multiple_choice import ChoiceManager

from aider.brade_prompts import CONTEXT_NOUN, THIS_MESSAGE_IS_FROM_APP

from .base_prompts import CoderPrompts

# Define the choice manager for analyzing architect responses
possible_architect_responses: ChoiceManager = ChoiceManager()

# Define the analysis choices used by the architect coder
response_section = possible_architect_responses.add_section(
    f"""Compare the assistant's response to the choices we gave it for how to respond. 
Decide whether the assistant's human partner will be best served by having the Brade 
application take one of the special actions, or by simply treating the assistant's response 
as conversation. Do this by choosing the single best option from the list below.

Select the **proposed changes** option if you think there's a reasonable chance the
user would like to interpret the assistants's answer as a proposal to make changes,
and would like to be able to say "yes" to it. This gives the assistant's human partner 
an opportunity to make that decision for themself. But if it is clear to you that the 
assistant has not proposed anything concrete enough to say "yes" to, then choose one of
the other options.
"""
)
architect_proposed_plan_changes = response_section.add_choice(
    "The assistant **proposed changes** to a plan document."
)
architect_proposed_non_plan_changes = response_section.add_choice(
    "The assistant **proposed changes** to project files beyond just a plan document."
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

    Attributes:
        main_model: The Model instance for the architect role
        editor_model: The Model instance for the editor role
    """

    def __init__(self, main_model, editor_model):
        """Initialize ArchitectPrompts with models for architect and editor roles.

        Args:
            main_model: The Model instance for the architect role
            editor_model: The Model instance for the editor role
        """
        super().__init__()
        self.main_model = main_model
        self.editor_model = editor_model

    def approved_non_plan_changes_prompt(self) -> str:
        """Get the prompt for approved non-plan changes."""
        return (
            "Please make those changes as you propose. When you are done making changes, stop and"
            " wait for input. After the Brade application has applied your changes to the project"
            " files, you will be prompted to review them."
        )

    def approved_plan_changes_prompt(self) -> str:
        """Get the prompt for approved plan changes."""
        return (
            "Please make the plan changes as you propose. When you are done making changes, stop"
            " and wait for input. After the Brade application has applied your changes to the"
            " project files, you will be prompted to review them. Then give me a chance to review"
            " our revised plan before you change any other files."
        )

    def review_changes_prompt(self) -> str:
        """Get the prompt for reviewing changes, conditionally adjusting instructions based on model type."""
        return f"""{THIS_MESSAGE_IS_FROM_APP}
Review your intended changes and the latest versions of the affected project files.

You can see your intended changes in SEARCH/REPLACE blocks in the chat above. You
use this special syntax, which looks like diffs or git conflict markers, to specify changes
that the Brade application should make to project files on your behalf.

If the process worked correctly, then the Brade application has applied those changes
to the latest versions of the files, which are provided for you in {CONTEXT_NOUN}. 
Double-check that the changes were applied completely and correctly.

Read with a fresh, skeptical eye.

{self._get_review_reasoning_instructions(self.main_model)}

Think about whether the updates fully and correctly achieve
the goals for this work. Think about whether any new problems were introduced,
and whether any serious existing problems in the affected content were left unaddressed.

{self._get_review_conclusions_instructions(self.main_model)}

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

    @property
    def changes_committed_message(self) -> str:
        """Get the message indicating that changes were committed."""
        return (
            THIS_MESSAGE_IS_FROM_APP
            + "The Brade application made those changes in the project files and committed them."
        )

    def _get_review_reasoning_instructions(self, model) -> str:
        """Get reasoning-specific instructions if the model is not a reasoning model.

        Args:
            model: The Model instance to check

        Returns:
            Reasoning instructions if needed, empty string otherwise.
        """
        if model.is_reasoning_model:
            return ""
        return (
            'Preface your response with the markdown header "# Reasoning". Then think out loud, '
            "step by step, as you review the affected portions of the modified files.\n"
        )

    def _get_review_conclusions_instructions(self, model) -> str:
        """Get conclusions-specific instructions if the model is not a reasoning model.

        Args:
            model: The Model instance to check

        Returns:
            Conclusions instructions if needed, empty string otherwise.
        """
        if model.is_reasoning_model:
            return ""
        return (
            "When you are finished thinking through the changes, mark your transition to "
            'your conclusions with a "# Conclusions" markdown header. Then, concisely explain '
            "what you believe about the changes.\n"
        )

    def _get_shared_response_instructions(self) -> str:
        """Get the shared instructions for all response types."""
        return """You can respond in any of the following three ways:

You can choose to just **respond conversationally** as part of your ongoing collaboration. 
In this case, the response you produce now will be your final output before
your partner has a chance to respond.

Alternatively, you have two ways to respond that will cause the Brade application to take
specific actions:

- You can **propose changes** that you would make as a next step.

  In this case, clearly state that you propose to edit project files. If it's not obvious from the
  discussion, explain your goals. In any case, briefly think aloud through any especially important 
  or difficult decisions or issues. Next, write clear, focused instructions for the changes. 
  Make these concrete enough to act on, but brief enough to easily review. Don't propose specific
  new code or other content at this stage. Conclude your response by asking your partner whether you 
  should make the changes you proposed.

  In this case, the response you produce now is just the first step of a multi-step process
  that will occur before your partner has a chance to respond with their own message. Don't end
  this response as though your partner will have a chance to speak next. Also, even if your
  partner has explicitly asked you to make changes, don't try to make them right now, in this
  Step 1. The only way you can actually make changes is to **propose changes** in this step and
  wait for your partner's approval.
  
  What will happen next is that the Brade application will ask your partner whether they want 
  you to go ahead and make file changes, (Y)es or (n)o. If they answer "yes", the Brade 
  application will walk you through steps 2 and 3 to actually make the changes and then
  review your own work. You will finish your response to your partner at the end of the 
  "review your work" step. Only then will your partner have a chance to speak.
  
- Or, you can ask to see more files. Provide the files' paths relative to the project root and 
  explain why you need them. In this case, the Brade application will ask your partner whether
  it is ok to provide those files to you."""

    def _get_base_instructions(self) -> str:
        """Get the base collaboration instructions."""
        return """Collaborate naturally with your partner. Together, seek ways to
make steady project progress through a series of small, focused steps. Try to do
as much of the work as you feel qualified to do well. Rely on your partner mainly
for review. If your partner wants you to do something that you don't feel you can
do well, explain your concerns and work with them on a more approachable next step.
Perhaps they need to define the task more clearly, give you a smaller task, do a 
piece of the work themselves, provide more context, or something else. Just be direct
and honest with them about your skills, understanding of the context, and high or
low confidence."""

    def _get_thinking_instructions(self) -> str:
        """Get instructions about taking time to think."""
        return """First decide whether to respond immediately or take time to think.

- You should respond immediately if you are very confident that you can give a simple,
  direct, and correct response based on things you already know.

- But if you are at all unsure whether your immediate answer would be correct, then you 
  should take time to think.

# Taking Time to Think

If you choose to take time to think, begin your response with a markdown header "# Reasoning".
Then think out loud, step by step, until you are confident you know the right answer."""

    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the 'architect' step of the architect workflow.

        This property must remain as the API expects, but we adapt instructions based on
        whether the main model is a reasoning model or not.
        """
        base_instructions = self._get_base_instructions()
        shared_response = self._get_shared_response_instructions()

        if self.main_model.is_reasoning_model:
            # For a reasoning model, we omit instructions about taking time to think
            response_choices = f"""
Right now, you are in [Step 1: a conversational interaction](#step-1-a-conversational-interaction)
of your [Three-Step Collaboration Flow](#three-step-collaboration-flow).

# Ways you Can Respond

{shared_response}"""
        else:
            # For a non-reasoning model, we include thinking instructions
            response_choices = f"""{self._get_thinking_instructions()}

# Ways you Can Respond

{shared_response}"""

        return f"{base_instructions}\n\n{response_choices}"

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
