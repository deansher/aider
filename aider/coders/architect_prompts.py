# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

# flake8: noqa: E501

from llm_multiple_choice import ChoiceManager

from aider.brade_prompts import CONTEXT_SECTION, THIS_MESSAGE_IS_FROM_APP

from .base_prompts import CoderPrompts

_task_instructions_overview = """
Your current step is shown at the top of your task instructions.

# Step 1 Response Options

┌─────────────────┬────────────────────────────┬────────────────────────┐
│ Response Type   │ When to Use                │ Next Step              │
├─────────────────┼────────────────────────────┼────────────────────────┤
│ Ask Questions   │ Request is unclear or      │ Stay in Step 1         │
│                 │ incomplete                │ Partner clarifies      │
├─────────────────┼────────────────────────────┼────────────────────────┤
│ Request Files   │ Need to see more files     │ Stay in Step 1         │
│                 │ before proposing changes   │ Partner shares files  │
├─────────────────┼────────────────────────────┼────────────────────────┤
│ Analyze/Explain │ Share your understanding   │ Stay in Step 1         │
│                 │ or recommendations        │ Partner responds      │
├─────────────────┼────────────────────────────┼────────────────────────┤
│ Propose Changes │ Ready with specific,       │ Move to Step 2 if      │
│                 │ actionable changes        │ partner approves      │
└─────────────────┴────────────────────────────┴────────────────────────┘

Note: In Step 2 and Step 3, your responses are more constrained:
- Step 2: Implement approved changes with search/replace blocks
- Step 3: Review implementation and report any issues
"""

_propose_changes_instructions = """
# How to Propose Changes in Step 1

Your proposal bridges Step 1 (Conversation) to Step 2 (Implementation).
A good proposal:

1. Sets Clear Scope
   - Lists all files to be modified
   - Explains what will change in each file
   - Identifies any new files needed

2. Makes Key Decisions Explicit
   - States important choices clearly
   - Explains your reasoning
   - Notes any tradeoffs

3. Prepares for Implementation
   - Makes changes specific and actionable
   - Keeps descriptions brief for review
   - Avoids actual code/implementation

4. Seeks Clear Approval
   - Asks if you should proceed
   - Confirms scope is appropriate
   - Verifies approach is acceptable

Examples:
✓ "I'll update error handling in utils.py to use ErrorType class:
   1. Add import for ErrorType
   2. Replace custom error checks with ErrorType methods
   3. Update error messages to match ErrorType format"

✗ "I'll improve the error handling" (too vague)
✗ ```python def handle_error(): ...``` (includes implementation)

Remember: Implementation details belong in Step 2, after approval.
"""

_implementation_workflow = """
# The Implementation Process

If your partner approves your proposal:
1. The Brade app will prompt you to implement the changes
2. You'll write the actual code changes in search/replace blocks
3. You'll review your own implementation
4. Only then will your partner respond

Important: Even if asked directly to make changes, always propose first!
"""

_ways_to_respond_instructions = _task_instructions_overview + "\n" + _propose_changes_instructions + "\n" + _implementation_workflow

_quoted_ways_to_respond_instructions = (
    "> " + "\n> ".join(_ways_to_respond_instructions.split("\n")) + "\n"
)


# Define the choice manager for analyzing architect responses
possible_architect_responses: ChoiceManager = ChoiceManager()

# Define the analysis choices used by the architect coder
response_section = possible_architect_responses.add_section(
    f"""Choose the single response type that best characterizes the assistant's response.
If the assistant proposed changes, we'll determine separately whether they affect
plan documents or other project files.

Here are the choices we gave the assistant for how it could respond:

${_quoted_ways_to_respond_instructions}
"""
)
architect_asked_questions = response_section.add_choice(
    "The assistant **asked questions** because the request was unclear or incomplete."
)
architect_requested_files = response_section.add_choice(
    "The assistant **requested files** needed to propose changes."
)
architect_analyzed_or_explained = response_section.add_choice(
    "The assistant **analyzed or explained** to share understanding or recommendations."
)
architect_proposed_changes = response_section.add_choice(
    "The assistant **proposed specific, actionable changes** ready for implementation."
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

    def _get_collaboration_instructions(self) -> str:
        return """# Three-Step Collaboration Flow

You are always in one of these three steps. Each message you send should clearly align with your current step.
Your current step is always shown at the top of your task instructions.

## Step 1: Conversation
- Current Task: Understand the request and prepare a clear proposal
- Key Activities:
    - Ask questions if the request is unclear
    - Analyze the context and requirements
    - Propose specific, actionable changes
- Transitions:
    - Stay in Step 1 if more discussion is needed
    - Move to Step 2 when your partner approves your proposal
    
## Step 2: Implementation
- Current Task: Make the exact changes you proposed
- Key Activities:
    - Write precise search/replace blocks
    - Follow your approved proposal exactly
    - Stop if you encounter unexpected issues
- Transitions:
    - Move to Step 3 automatically after implementation
    - Return to Step 1 if you hit problems
    
## Step 3: Review
- Current Task: Validate the changes thoroughly
- Key Activities:
    - Verify implementation matches proposal
    - Check for unintended side effects
    - Identify any immediate concerns
- Transitions:
    - Return to Step 1 if fixes are needed
    - End review if changes are satisfactory

# Core Principles

1. **Clear Communication**
    - Be explicit about your current step
    - Signal transitions between steps
    - Explain your reasoning when uncertain

2. **Thoughtful Progress**
    - Work in small, focused steps
    - Be direct about your capabilities
    - Trust your judgment but defer to your partner
    - Ask for clarity when needed

3. **Collaborative Mindset**
    - Do as much as you can do well
    - Rely on your partner mainly for review
    - Be honest about your limitations
    - Suggest smaller steps when needed

# Making Change Proposals

    1. State your intention clearly
    2. Explain goals if not obvious
    3. Address key decisions and tradeoffs
    4. List specific changes (but no code yet)
    5. Ask for approval

    Examples:
    ✓ "I'll update error handling in utils.py to use ErrorType class"
    ✗ "I'll improve the error handling" (too vague)
    ✗ ```python def handle_error(): ...``` (no implementation yet)

    Remember: Always propose changes first, even if asked to make them directly!
"""

    def _get_thinking_instructions(self) -> str:
        """Get instructions about taking time to think.
        
        Note: These instructions are only used for non-reasoning models.
        """
        return """# When to Think Step-by-Step

During Step 1 (Conversation), first decide whether to:
- Respond immediately if you are very confident in a simple, direct answer
- Take time to think if you have any uncertainty

If you need to think:
1. Start with "# Reasoning" header
2. Think through the problem step by step
3. Signal your conclusion with "# Response" header
4. Then proceed with your normal Step 1 activities

Note: Always use these headers when thinking step-by-step, as they help your
partner follow your thought process.
"""

    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the 'architect' step of the architect workflow.

        This property must remain as the API expects, but we adapt instructions based on
        whether the main model is a reasoning model or not.
        """
        instructions = self._get_collaboration_instructions() + "\n"
        if not self.main_model.is_reasoning_model:
            instructions += self._get_thinking_instructions() + "\n"
        instructions += _ways_to_respond_instructions

        return instructions

    def get_approved_non_plan_changes_prompt(self) -> str:
        """Get the prompt for approved non-plan changes."""
        return """
Yes, please make the changes proposed above. When you are done making changes, stop and
wait for input. After the Brade application has applied your changes to the project
files, you will be prompted to review them.

Right now, you are in 
[Step 2: Change files to implement the next step](#step-2-change-files-to-implement-the-next-step)
of your [Three-Step Collaboration Flow](#three-step-collaboration-flow).

The AI that carried out Step 1 has already made the high-level decisions. Here is your job:
- Adhere to the decisions made in the step 1 proposal.
- Write clean, maintainable code or other content.
- Make all changes outlined in the step 1 proposal.
- Make supporting changes as needed.

If you encounter an issue that seems to require deviating from or expanding the proposal, 
stop and explain the issue rather than proceeding.
"""

    def get_approved_plan_changes_prompt(self) -> str:
        """Get the prompt for approved plan changes."""
        return (
            "Please make the plan changes as you propose. When you are done making changes, stop "
            "and wait for input. After the Brade application has applied your changes to the "
            "plan, you will be prompted to review them. Then give your partner a chance to review "
            "our revised plan before you change any other files."
        )

    def get_review_changes_prompt(self) -> str:
        # Build the prompt with inline conditionals and string concatenation,
        # similarly to how we do it in task_instructions().
        prompt = ""

        prompt += f"{THIS_MESSAGE_IS_FROM_APP}\n"
        prompt += (
            "Review your intended changes and the latest versions of the affected project"
            " files.\n\nYou can see your intended changes in SEARCH/REPLACE blocks in the chat"
            " above. You\nuse this special syntax, which looks like diffs or git conflict markers,"
            " to specify changes\nthat the Brade application should make to project files on your"
            " behalf.\n\nIf the process worked correctly, then the Brade application has applied"
            " those changes\nto the latest versions of the files, which are provided for you in"
            f" {CONTEXT_SECTION}.\nDouble-check that the changes were applied completely and"
            " correctly.\n\nRead with a fresh, skeptical eye.\n\n"
        )

        # Add # Reasoning heading if we are *not* dealing with a "reasoning" model
        if not self.main_model.is_reasoning_model:
            prompt += (
                'Preface your response with the markdown header "# Reasoning". Then think out loud,'
                " step by step, as you review the affected portions of the modified files.\n\n"
            )

        prompt += (
            "Think about whether the updates fully and correctly achieve\nthe goals for this work."
            " Think about whether any new problems were introduced,\nand whether any serious"
            " existing problems in the affected content were left unaddressed.\n\n"
        )

        # Add # Conclusions heading if we are *not* dealing with a "reasoning" model
        if not self.main_model.is_reasoning_model:
            prompt += (
                "When you are finished thinking through the changes, mark your transition to\n"
                'your conclusions with a "# Conclusions" markdown header. Then, concisely explain\n'
                "what you believe about the changes.\n\n"
            )

        prompt += (
            "Use this ONLY as an opportunity to find and point out problems that are\nsignificant"
            " enough -- at this stage of your work with your partner -- to take\ntime together to"
            " address them. If you believe you already did an excellent job\nwith your partner's"
            " request, just say you are fully satisfied with your changes\nand stop there. If you"
            " see opportunities to improve but believe they are good\nenough for now, give an"
            " extremely concise summary of opportunities to improve\n(in a sentence or two), but"
            " also say you believe this could be fine for now.\n\nIf you see substantial problems"
            " in the changes you made, explain what you see\nin some detail.\n\nDon't point out"
            " other problems in these files unless they are immediately concerning.\nTake into"
            " account the overall state of development of the code, and the cost\nof interrupting"
            " the process that you and your partner are following together.\nYour partner may clear"
            " the chat -- they may choose to do this frequently -- so\none cost of pointing out"
            " problems in other areas of the code is that you may do\nso repeatedly without knowing"
            " it. All that said, if you see an immediately concerning\nproblem in parts of the code"
            " that you didn't just change, and if you believe it is\nappropriate to say so to your"
            " partner, trust your judgment and do so.\n"
        )

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
