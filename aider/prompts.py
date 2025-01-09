# flake8: noqa: E501


# COMMIT

from aider.brade_prompts import THIS_MESSAGE_IS_FROM_APP

commit_message_prompt = """<brade:commit_message_guidelines>

Start your response with the first line of the commit message:
- Provides a concise summmary of the changes (max 50 chars)
- Use imperative mood (\"Add feature\" not \"Added feature\")

You can then add a few more lines to provide more detail if needed.

## Examples of Good Commit Messages

### Good
Add XML namespace to test assertions

### Good
Update test to use brade: namespace prefix for consistency.

### Good: Usefully Multi-line
Add test for system message cache control

in AnthropicChatModelProvider.test.ts, verify that system messages with cache control are 
properly handled in _chatHistoryToAnthropic.

## Examples of Bad Commit Messages

### Bad: Conversational
I updated the tests to use proper XML namespaces

### Bad: Wrong Mood
Adding XML namespaces to tests

### Bad: Has Preface that Should be Omitted
**Commit Message**
Add XML namespace to test assertions

### Bad: Has Preface that Should be Omitted
Here is the commit message for the changes:

Add type guard for WireMessage.content

In AnthropicChatModelProvider.ts, update the _formatWireMessage function to handle
both string and array cases for the WireMessage.content property.

This fixes a TypeScript error where we were trying to use flatMap on a string, which
is not a valid operation.

### Bad: Too Long
Fix system message cache control in _chatHistoryToAnthropic

The key changes are:

1. In the `system` message formatting, we use `map` instead of `flatMap` to ensure the cache control is applied to each message.
2. We use a conditional expression to only include the `cache_control` property if `includeCacheControl` is true and the message has a `cacheControl` property.

This ensures that the system messages are properly formatted with the cache control information when it is available and the caller has requested it.

Additionally, I've added a new test case to verify the behavior when cache control is included and when it is not included:

```typescript
it('should handle system message cache control', () => {
  const messages: Message[] = [
    {
      role: 'system',
      content: 'System instruction.',
      cacheControl: EPHEMERAL_CACHE_CONTROL
    }
  ];
</brade:commit_message_guidelines>

Generate a Git commit message for the changes shown in <diffs>...</diffs>.

Pay careful attention to whether these changes implement new features, revise or improve
our planning document(s), or revise or improve other documents. Write your commit message
in a way that makes this clear. 

Respond with just the commit message, without preface, explanation, or any other text.
We will use your response as a commit message exactly as you write it. 
Use your judgment as a senior software engineer to write a great commit message.
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
