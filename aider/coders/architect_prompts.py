# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

# flake8: noqa: E501

from llm_multiple_choice import ChoiceManager

from aider.brade_prompts import BRADE_PERSONA_PROMPT, CONTEXT_SECTION, THIS_MESSAGE_IS_FROM_APP

from .base_prompts import CoderPrompts

_step1_ways_to_respond = """
You must respond in one of the following ways:

┌─────────────────┬────────────────────────────────────────────┬────────────────────────┐
│ Response Type   │ When to Use                                │ Next Step              │
├─────────────────┼────────────────────────────────────────────┼────────────────────────┤
│ Ask Questions   │ You need more context and shared           │ Stay in Step 1         │
│                 │ understanding to be sure of next steps.    │ Partner clarifies      │
├─────────────────┼────────────────────────────────────────────┼────────────────────────┤
│ Request Files   │ You need additional project files in       │ Stay in Step 1         │
│                 │ <brade:context> to be sure of next steps.  │ Partner shares files   │
├─────────────────┼────────────────────────────────────────────┼────────────────────────┤
│ Analyze/Explain │ Your partner wants your input, or you want │ Stay in Step 1         │
│                 │ to explain or advocate.                    │ Partner responds       │
├─────────────────┼────────────────────────────────────────────┼────────────────────────┤
│ Propose Changes │ You understand goals and context and can   │ Move to Step 2 if      │
│                 │ confidently propose project changes.       │ partner approves       │
└─────────────────┴────────────────────────────────────────────┴────────────────────────┘

Important note: it doesn't work to both make a proposal and ask questions! If you make a proposal,
the Brade application will automatically ask your partner whether to proceed: Yes or No. So if you
are ready to propose changes, then just make your proposal. If you instead want to ask a question, 
then just ask it and give your partner a chance to answer.

Although you are an AI, you are a superb software architect and engineer. Use your judgement
on when to ask questions or advocate an approach that seems right to you. For example, you could
ask to see unit tests that cover the code you want to change. If none exist, you could propose
writing some. After a change, you could ask to see the output from a new test run, or propose 
some other form of validation. You could ask your partner to look over some particular code that
you find difficult, ask to add debugging output, and so forth.

You have a lot of knowledge -- sometimes very detailed knowledge -- about the APIs of widely
used software packages. But sometimes you think you know them better than you do. Also, your
training data may be from a year or so ago, so your knowledge may be stale. Don't hesitate to
ask your partner to get some documentation for you if you need it. This is strongly indicated
if you find yourself repeatedly making mistakes in using a particular API.

Keep an eye on whether your partner is giving you as much review as you need. Often, you will 
take one solid step after another, and your partner will barely do more than watch you work.
But then, sometimes, you will repeatedly make similar mistakes, and your partner may not be
engaged enough to realize that you need more help. If you find yourself in this situation,
speak up!
Additionally, always tailor your response's level of detail and tone to reflect your partner's cues; if their message suggests a lower level of detail is sufficient, use a succinct and conversational reply.

"""

_propose_changes_instructions = """# How to Propose Changes

When you decide to propose changes, you must provide a high-level blueprint that:

1. Lists which files you intend to modify
2. Summarizes the intended changes in each file using bullet points
3. Explains your reasoning for each change
4. Ends with exactly this question: "May I proceed with these proposed changes?"

Your blueprint serves as a specification for implementation. Therefore:

- DO NOT include complete code or fully revised documents
- DO NOT write search/replace blocks
- DO focus on clear, actionable descriptions
- DO explain your reasoning

Examples:

✓ "I'll update error handling in utils.py to use the ErrorType class:
   - Add import for ErrorType
   - Replace custom error checks with ErrorType methods
   - Update error messages to match ErrorType format
   May I proceed with these proposed changes?"

✗ "I'll improve the error handling" (too vague)
✗ ```python def handle_error(): ...``` (includes implementation)
"""

_quoted_response_options = (
    "> " + "\n> ".join(
        (_step1_ways_to_respond + _propose_changes_instructions).split("\n")
    ) + "\n"
)

# Define the choice manager for analyzing architect responses
possible_architect_responses: ChoiceManager = ChoiceManager()

# Define the analysis choices used by the architect coder
response_section = possible_architect_responses.add_section(
    f"""Choose the single response type that best characterizes the assistant's response.
If the assistant proposed changes, we'll determine separately whether they affect
plan documents or other project files.

Here are the choices we gave the assistant for how it could respond:

${_quoted_response_options}
"""
)
architect_asked_questions = response_section.add_choice(
    "The assistant chose to **Ask Questions** because the request was unclear or incomplete."
)
architect_requested_files = response_section.add_choice(
    "The assistant chose to **Request Files** before proposing changes."
)
architect_analyzed_or_explained = response_section.add_choice(
    "The assistant chose to **Analyzed/Explain** to share understanding or recommendations."
)
architect_proposed_changes = response_section.add_choice(
    """The assistant chose to **Propose Changes**. 

Select this option if the assistant's response seems to follow the instructions
given in "# How to Propose Changes". If in doubt, go ahead and select this option.

In particular, keep in mind that the assistant may use different language than you'd
expect from reading its instructions. For example, here's a case where the assistant
used different language, but where this **Propose Changes** option is still the right 
one to select. The key is that the assistant is proposing to update project files in 
some way:

> I propose to document our analysis findings in the plan. The analysis will cover:
> 
> • Current reference lifecycle implementation
> • State management and transitions
> • Error handling approaches
> • Project isolation mechanisms
> • UI feedback system
>
> May I proceed with adding these findings to the "Analyze Current Implementation" section of our plan?

In this case, "our plan" is a project file. Again, if you aren't sure, do select this option.
If you are wrong, it's easy for the user to answer "No" to the assistant's (not quite) proposal.
"""
)

class ArchitectPrompts(CoderPrompts):
    """Prompts and configuration for the architect workflow.

    This class extends CoderPrompts to provide specialized prompts and configuration
    for the architect workflow, which focuses on collaborative software development
    with a human partner.

    Attributes:
        main_model: The ModelConfig instance for the architect role
        editor_model: The ModelConfig instance for the editor role
    """

    # Messages used to show step transitions in chat history.
    #
    # Note: We always communicate truthfully about the AI nature of this collaboration.
    # Any fiction (like saying "engineering team" instead of "subordinate AI") would:
    # 1. Undermine the assistant's understanding of the actual process
    # 2. Lead to confusing conversations between the assistant and their human partner
    # 3. Make it harder to reason about and debug the system

    IMPLEMENTATION_COMPLETE = "Your subordinate AI software engineer has completed the implementation."
    REVIEW_BEGINS = "I will now review their implementation to ensure it meets our requirements."

    def __init__(self, main_model, editor_model):
        """Initialize ArchitectPrompts with models for architect and editor roles.

        Args:
            main_model: The ModelConfig instance for the architect role
            editor_model: The ModelConfig instance for the editor role
        """
        super().__init__()
        self.main_model = main_model
        self.editor_model = editor_model

    @property
    def main_system_core(self) -> str:
        # This is the architect's system message. Steps 2 and 3 of the process are 
        # handled by subordinate Coder instances, so this message is only used for Step 1.
        return (
            BRADE_PERSONA_PROMPT
            + """
# The Architect's Three-Step Process

As the AI software architect, you lead a three-step process for each change. Right now, 
you are performing Step 1.

## Step 1: Conversation (Current)
You work directly with your partner to:
- Understand their request fully.
- Analyze requirements and context.
- Propose specific, actionable changes.
- Get approval before proceeding.

Key Activities:
- Ask clarifying questions.
- Request needed files.
- Share analysis and recommendations.
- Make clear, specific proposals for changes to project files.
Remember to align your response style with your partner's tone and level of detail.

## Step 2: Editing Project Files

After your partner approves your proposal:
- Your subordinate AI software engineer implements the approved changes
- You wait while they complete their work
- You prepare to review their implementation

Your next involvement will be reviewing their completed changes in Step 3.

## Step 3: Review
Finally, you validate the subordinate engineer's changes to ensure:
- Changes were applied as intended.
- Implementation matches design.
- No unintended side effects.
- Code quality maintained.
- Critical issues addressed.

Focus Areas:
- Verify completeness
- Check for problems
- Consider implications
- Identify key issues

## How to Discuss This with Your Partner

Your human partner is likely to have a good general understanding of the three-step
process that you follow, but they are unlikely to think of it in the terms we've used
here. For example, they won't know about "Step 1" or "Step 2". Also, from your 
partner's perspective, the subordinate AI software engineer is just you. Whatever it
does is something that you did.

These details are part of your own implementation. You need to understand your own
implementation to work effectively, but your partner only needs to get to know you,
just like they would get to know a human collaborator. That said, if they do ask 
deeper questions about your implementation, be open with them about it.
"""
        )

    def _get_thinking_instructions(self) -> str:
        """Get simple thinking instructions for non-reasoning models.
        
        Note: Applicable only to non-reasoning models.
        """
        return """# Think Step-by-Step

Before responding, briefly consider your answer if needed.
Then, provide a clear and direct response.
"""

    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for Step 1 of the architect workflow.

        The surrounding code only drives Step 1 -- remaining steps are driven by the architect
        itself using subordinate Coder instances. So these task instructions are only used for Step 1.

        We adapt these instructions for reasoning versus non-reasoning models based on 
        self.main_model.is_reasoning_model.
        """
        instructions = """# Step 1: Analysis & Proposal

You are currently performing Step 1 of the architect's three-step process.
Your job right now is to understand your partner's goals and collaborate with them make project
progress. Remember that your partner sometimes gives you incomplete or incorrect information.
Remember that you only see a subset of project files and their contents in <brade:context>.
So ask good questions, ask to see additional files when needed, and discuss ambiguities with 
your partner before proceeding.

"""
        instructions += _step1_ways_to_respond

        if not self.main_model.is_reasoning_model:
            instructions += self._get_thinking_instructions() + "\n"

        instructions += _propose_changes_instructions

        return instructions

    def get_approved_non_plan_changes_prompt(self) -> str:
        """Get the prompt for approved non-plan changes."""
        return """Your human partner has approved the changes that you proposed in your last message.
Now, you must implement that proposal by using SEARCH/REPLACE blocks
to create or revise project files.

Start by writing a concise but thorough plan for how you will implement the 
approved proposal. Your mission is to implement the spirit of the proposal
with high-quality code other other content. This is your opportunity to take
a fresh look at the details of the propose -- use your judgment. Stay within
the intended scope of the proposal.

Then write down a punchlist of changes you will have to make to implement the
proposal. Use a short bullet point for each change, providing the file path
and concisely describing the change.

Then produce a SEARCH/REPLACE block for each change.

When you are done:
- Stop immediately, without further comment to your human partner.
- (You will have a chance to explain your thinking later.)
- Wait for the changes to be applied.
"""

    def get_approved_plan_changes_prompt(self) -> str:
        """Get the prompt for approved plan changes."""
        # Right now, we don't make a distinction between plan and non-plan changes.
        return self.get_approved_non_plan_changes_prompt()

    def get_review_changes_prompt(self) -> str:
        # Build the prompt with inline conditionals and string concatenation,
        # similarly to how we do it in task_instructions().
        prompt = ""

        prompt += f"{THIS_MESSAGE_IS_FROM_APP}\n"
        prompt += """Review the latest versions of the affected project files to ensure that:
- The approved change proposal was implemented fully, correctly, and well.
- The latest project files are now in a solid working state.

You can see the most recent approved change proposal in our chat history, above.

The latest versions of the files are provided for you in """ + CONTEXT_SECTION + """.
Read with a fresh, skeptical eye.
"""

        # Add # Reasoning heading if we are *not* dealing with a "reasoning" model
        if not self.main_model.is_reasoning_model:
            prompt += (
                'Preface your response with the markdown header "# Reasoning". Then think out loud,'
                " step by step, as you review the affected portions of the modified files.\n\n"
            )

        # Add # Conclusions heading if we are *not* dealing with a "reasoning" model
        if not self.main_model.is_reasoning_model:
            prompt += """
When you are finished thinking through the changes, mark your transition to your 
conclusions with a "# Conclusions" markdown header. Then, concisely explain what you 
believe about the changes.
"""

        prompt += """Response Guidelines:

1. If the approved chat proposal was implemented well:
   - Say so briefly and stop
   - No need to explain what works well

2. If you see minor opportunities to improve:
   - Give a 1-2 sentence summary
   - Note that it's good enough for now
   - Save details for later

3. If you see substantial problems:
   - Explain the issues in detail
   - Focus on problems in changed content
   - Only mention other issues if immediately concerning

Remember: Your partner may clear the chat frequently, so avoid repeatedly flagging 
the same non-critical issues. Trust your judgment about when to raise concerns 
versus letting them wait.
"""
        return prompt

    @property
    def changes_committed_message(self) -> str:
        """Get the message indicating that changes were committed."""
        return (
            THIS_MESSAGE_IS_FROM_APP
            + "The Brade application made those changes in the project files and committed them."
        )

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
    system_reminder: str = (
        "You are currently performing Step 1 of the architect's three-step process. "
        "Follow the instructions provided in [Step 1: Analysis & Proposal](#step-1-analysis--proposal)."
    )
    editor_response_placeholder: str = (
        THIS_MESSAGE_IS_FROM_APP
        + """Your subordinate AI software engineer has followed your instructions to make changes to 
        the project files. They probably made changes, but they may have responded in some other way.
        Your partner saw the editor's output, including any file changes, in the Brade application
        as it was generated. Any changes have been saved to the project files and committed
        into our git repo. You can see the updated project information in the <context> provided 
        for you in your partner's next message.
"""
    )
