# flake8: noqa: E501


# COMMIT

from aider.brade_prompts import THIS_MESSAGE_IS_FROM_APP

commit_message_prompt = """You are an expert software engineer. Write a concise,
one-line git commit message for the file changes shown below in <diffs>...</diffs>. 
Respond with nothing but the one-line commit message, without any additional text, 
explanations, or line breaks.

Ensure the commit message:
- Is in the imperative mood (e.g., \"Add feature\" not \"Added feature\" or \"Adding feature\").
- Does not exceed 72 characters.
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
