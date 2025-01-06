# flake8: noqa: E501


# COMMIT

from aider.brade_prompts import THIS_MESSAGE_IS_FROM_APP

commit_message_prompt = """Generate a Git commit message for the changes shown in <diffs>...</diffs>.
Respond with just the commit message, without preface, explanation, or any other text.
We will use your response as a commit message exactly as you write it.

Requirements:
- Use imperative mood (\"Add feature\" not \"Added feature\")
- Max 50 chars for first line
- Optional details after blank line
- Focus on what changed and why

Example good messages:
    Add XML namespace to test assertions
    
    Update test to use brade: namespace prefix for consistency.

    Fix factorial implementation
    
    Replace recursive implementation with math.factorial
    for better performance and reliability.

Example bad messages:
    \"I updated the tests to use proper XML namespaces\"  # conversational
    \"Adding XML namespaces to tests\"  # wrong mood
    \"This commit adds XML namespaces\"  # too wordy
"""

# COMMANDS
undo_command_reply = (
    THIS_MESSAGE_IS_FROM_APP
    + """Your partner had us discard the last edits. We did this with `git reset --hard HEAD~1`.
Please wait for further instructions before attempting that change again. You may choose to ask
your partner why they discarded the edits.
"""
)

added_files = THIS_MESSAGE_IS_FROM_APP + """Your partner added these files to the chat: {fnames}
Tell them if you need additional files.
"""

run_output = """I ran this command:

{command}

And got this output:

{output}
"""

# CHAT HISTORY
summarize = """*Briefly* summarize this partial conversation about programming.
Include less detail about older parts and more detail about the most recent messages.
Start a new paragraph every time the topic changes!

This is only part of a longer conversation so *DO NOT* conclude the summary with language like "Finally, ...". Because the conversation continues after the summary.
The summary *MUST* include the function names, libraries, packages that are being discussed.
The summary *MUST* include the filenames that are being referenced by the assistant inside the ```...``` fenced code blocks!
The summaries *MUST NOT* include ```...``` fenced code blocks!

Phrase the summary with the USER in first person, telling the ASSISTANT about the conversation.
Write *as* the user.
The user should refer to the assistant as *you*.
Start the summary with "I asked you...".
"""

summary_prefix = "I spoke to you previously about a number of things.\n"
