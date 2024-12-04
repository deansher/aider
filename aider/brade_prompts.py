# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

"""Functions for formatting chat messages according to Brade's prompt structure.

This module implements Brade's approach to structuring prompts for LLM interactions.
It follows the guidelines in design_docs/anthropic_docs/claude_prompting_guide.md:
"""

from enum import Enum
from typing import Tuple

from .types import ChatMessage


class ContextMessagePlacement(Enum):
    """Controls which message gets context and task elements.

    Values:
        FINAL_USER_MESSAGE: Add context and task elements to the final user message.
            This is currently the only supported option.
        INITIAL_USER_MESSAGE: Add context and task elements to the first user message.
            This option is not yet supported.
    """
    FINAL_USER_MESSAGE = "final_user_message"
    INITIAL_USER_MESSAGE = "initial_user_message"


class ContextPositionInMessage(Enum):
    """Controls where in the message context and task elements are placed.

    Values:
        PREPEND: Add context and task elements at the start of the message.
            This is currently the only supported option.
        INSERT: Add context and task elements after the first line of the message.
            This option is not yet supported.
    """
    PREPEND = "prepend"
    INSERT = "insert"


CONTEXT_NOUN = "<context>...</context>"

TASK_INSTRUCTIONS_NOUN = "<task_instructions>...</task_instructions>"

TASK_EXAMPLES_NOUN = "<task_examples>...</task_examples>"

BRADE_PERSONA_PROMPT = f"""You are Brade, a highly skilled and experienced AI software engineer.
You are implemented on top of a variety of LLMs from a combination of OpenAI and Anthropic.
You are collaborating with a human programmer in a terminal application called Brade.

# How You Collaborate with Your Partner

You defer to your human partner's leadership. That said, you also trust your own judgment and want
to get the best possible outcome. So you challenge your partner's decisions when you think that's
important. You take pride in understanding their context and goals and collaborating effectively
at each step. You are professional but friendly.

You thoughtfully take into account your relative strengths and weaknesses.

## You have less context than your human partner.

Your human partner is living the context of their project, while you only know what they
tell you and provide to you in the chat. Your partner will try to give you the context they
need, but they will often leave gaps. It is up to you to decide whether you have enough context
and ask follow-up questions as necessary before beginning a task.

## You write code much faster than a human can.

This is valuable! However it can also flood your partner with more code than they
have the time or emotional energy to review.

## You make mistakes.

You and your human partner both make mistakes. You must work methodically, and then
carefully review each others' work.

## Your human partner has limited time and emotional energy.

Their bandwidth to review what you produce is often the key bottleneck in your
work together. Here are the best ways to maximize your partner's bandwidth:

* Before you begin a task, ask whatever follow-up questions are necessary to obtain clear
  instructions and thorough context, and to resolve any ambiguity.

* Begin with concise deliverables that your partner can quickly review to
  make sure you have a shared understanding of direction and approach. For example,
  if you are asked to revise several functions, then before you start the main
  part of this task, consider asking your partner to review new header comments
  and function signatures.

* In all of your responses, go straight to the key points and provide the
  most important information concisely.

# Your Core Beliefs about Software Development

You believe strongly in this tenet of agile: use the simplest approach that might work.

You judge code primarily with two lenses:

1. You want the code's intent to be clear with as little context as feasible.
   For example, it should use expressive variable names and function names to make
   its intent clear.

2. You want a reader of the code to be able to informally prove to themselves
   that the code does what it intends to do with as little additional context as feasible.

You try hard to make the imperative portions of the code clear enough that comments
are unnecessary. You take the time to write careful comments for APIs such as function
signatures and data structures. You pay attention to documenting invariants and then
consistently maintaining them.

# How the Brade Application Works

Your partner interacts with the Brade application in a terminal window. They see your
replies there also. The two of you are working in the context of a git repo. Your partner
can see those files in their IDE or editor. They must actively decide to show you files
before you can see entire file contents. However, you are always provided with a map
of the repo's content. If you need to see files that your partner has not provided, you
should ask for them.

# Three-Step Collaboration Flow

## Step 1: a conversational interaction

First, you carefully review:
   - The task instructions and examples in the current message
   - The repository map showing the codebase structure
   - The content of files you've been given access to
   - The platform information about the development environment
   - The conversation history for additional context

Then you respond as appropriate, in ways such as the following:
   - Ask follow-up questions if you need more context.
   - Propose a solution and wait for your partner's feedback.
   - Propose how you would change files to implement the next step.
   - Share your analysis and recommendations.

## Step 2: Change files to implement the next step

If you propose a solution and your partner approves it, then you can make changes to
project files. You do this by creating "search/replace blocks". You can only do it in
this Step 2. Carefully follow the instructions in {TASK_INSTRUCTIONS_NOUN}.

## Step 3: Review your work

Finally, you look over your file changes and either tell your partner that they
look good to you or explain any concerns.

# Context and Task Information Prepended to Final User Message

In the final user message, before your partner's response to you, we prepend context
and task information. This information is not visible to your partner. It is organized
as follows:

```
<context>
  <!-- Repository overview and structure -->
  <repository_map>
    Repository map content appears here, using existing map formatting.
  </repository_map>

  <!-- Project source files -->
  <!-- Read-only reference files -->
  <readonly_files>
    <file path="path/to/file.py">
      <content>
def hello():
    print("Hello & welcome!")
    if x < 3:
        return True
      </content>
    </file>
  </readonly_files>

  <!-- Files available for editing -->
  <editable_files>
    <file path="path/to/other_file.py">
      <content>
def goodbye(name):
    print(f"Goodbye Brade!")
      </content>
    </file>
  </editable_files>

  <!-- System environment details -->
  <platform_info>
    Operating system, shell, language settings, etc.
  </platform_info>
</context>

<!-- Task-specific instructions and examples -->
<task_instructions>
  Current task requirements, constraints, and workflow guidance.
</task_instructions>

<task_examples>
  Example conversation demonstrating desired behavior for this task.
    <!-- Example interactions demonstrating desired behavior -->
    <example>
      <message role="user">Example user request</message>
      <message role="assistant">Example assistant response</message>
    </example>
</task_examples>
```
"""

THIS_MESSAGE_IS_FROM_APP = (
    """This message is from the Brade application, rather than from your partner.
Your partner does not see this message.

"""
)

REST_OF_MESSAGE_IS_FROM_APP = (
    """(The rest of this message is from the Brade application, rather than from your partner.
Your partner does not see this portion of the message.)

"""
)


def format_task_examples(task_examples: list[ChatMessage] | None) -> str:
    """Formats task example messages into XML structure.

    This function validates and transforms example conversations into XML format,
    showing paired user/assistant interactions that demonstrate desired behavior.

    Args:
        task_examples: List of ChatMessages containing example conversations.
            Messages must be in pairs (user, assistant) demonstrating desired behavior.
            Can be None to indicate no examples.

    Returns:
        XML formatted string containing the example conversations.
        Returns empty string if no examples provided.

    Raises:
        ValueError: If messages aren't in proper user/assistant pairs
            or if roles don't alternate correctly.
    """
    if not task_examples:
        return ""

    # Validate and transform task examples
    if len(task_examples) % 2 != 0:
        raise ValueError("task_examples must contain pairs of user/assistant messages")

    examples_xml = ""
    for i in range(0, len(task_examples), 2):
        user_msg = task_examples[i]
        asst_msg = task_examples[i + 1]

        if user_msg["role"] != "user" or asst_msg["role"] != "assistant":
            raise ValueError("task_examples must alternate between user and assistant messages")

        examples_xml += (
            "<example>\n"
            f"<message role='user'>{user_msg['content']}</message>\n"
            f"<message role='assistant'>{asst_msg['content']}</message>\n"
            "</example>\n"
        )

    return wrap_xml("task_examples", examples_xml)


# Type alias for file content tuples (filename, content)
FileContent = Tuple[str, str]


def wrap_xml(tag: str, content: str | None) -> str:
    """Wraps content in XML tags, always including tags even for empty content.

    The function ensures consistent newline handling:
    - A newline after the opening tag
    - For non-empty content: exactly one newline at the end of the content
    - For empty/whitespace content: no additinal newline, so the opening and closing tags
      are on adjacent lines
    - A newline after the closing tag

    Args:
        tag: The XML tag name to use
        content: The content to wrap, can be None/empty

    Returns:
        The wrapped content with tags, containing empty string if content is None/empty
    """
    if not content:
        content = ""

    # Handle whitespace-only content
    if not content.strip():
        return f"<{tag}>\n</{tag}>\n"

    stripped_content = content.rstrip('\n')
    return f"<{tag}>\n{stripped_content}\n</{tag}>\n"


def format_file_section(files: list[FileContent] | None) -> str:
    """Formats a list of files and their contents into an XML section.

    Args:
        files: List of FileContent tuples, each containing:
            - filename (str): The path/name of the file
            - content (str): The file's content

    Returns:
        XML formatted string containing the files and their contents

    Raises:
        TypeError: If files is not None and not a list of FileContent tuples
        ValueError: If any tuple in files doesn't have exactly 2 string elements
    """
    if not files:
        return ""

    if not isinstance(files, list):
        raise TypeError("files must be None or a list of (filename, content) tuples")

    result = ""
    for item in files:
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("Each item in files must be a (filename, content) tuple")

        fname, content = item
        if not isinstance(fname, str) or not isinstance(content, str):
            raise ValueError("Filename and content must both be strings")

        result += f"<file path='{fname}'>\n{content}\n</file>\n"
    return result


def format_brade_messages(
    system_prompt: str,
    task_instructions: str,
    done_messages: list[ChatMessage],
    cur_messages: list[ChatMessage],
    repo_map: str | None = None,
    readonly_text_files: list[FileContent] | None = None,
    editable_text_files: list[FileContent] | None = None,
    image_files: list[FileContent] | None = None,
    platform_info: str | None = None,
    task_examples: list[ChatMessage] | None = None,
    context_message_placement: ContextMessagePlacement = ContextMessagePlacement.FINAL_USER_MESSAGE,
    context_position: ContextPositionInMessage = ContextPositionInMessage.PREPEND,
) -> list[ChatMessage]:
    """Formats chat messages according to Brade's prompt structure.

    This function implements Brade's approach to structuring prompts for LLM interactions.
    It organizes the context and messages following Claude prompting best practices:
    - Single focused system message for role/context
    - Supporting material in XML sections
    - Clear separation of context and user message
    - Consistent document organization

    Args:
        system_prompt: Core system message defining role and context
        done_messages: Previous conversation history
        cur_messages: Current conversation messages
        repo_map: Optional repository map showing structure and content
        readonly_text_files: Optional list of (filename, content) tuples for reference text files
        editable_text_files: Optional list of (filename, content) tuples for text files being edited
        image_files: Optional list of (filename, content) tuples for image files
        platform_info: Optional system environment details
        task_instructions: task-specific requirements and workflow guidance
        task_examples: Optional list of ChatMessages containing example conversations.
            These messages will be transformed into XML format showing example interactions.
            Messages should be in pairs (user, assistant) demonstrating desired behavior.

    Returns:
        The formatted sequence of messages ready for the LLM

    Raises:
        ValueError: If system_prompt is None or if task_examples are malformed
        TypeError: If file content tuples are not properly formatted
    """
    if system_prompt is None:
        raise ValueError("system_prompt cannot be None")

    if context_message_placement != ContextMessagePlacement.FINAL_USER_MESSAGE:
        raise ValueError("Only FINAL_USER_MESSAGE placement is currently supported")

    if context_position != ContextPositionInMessage.PREPEND:
        raise ValueError("Only PREPEND position is currently supported")

    # Build the context section
    context_parts = []

    # Add repository map if provided and contains non-whitespace content
    if repo_map and repo_map.strip():
        context_parts.append(wrap_xml("repository_map", repo_map))

    # Add file sections if provided
    if readonly_text_files:
        files_xml = format_file_section(readonly_text_files)
        context_parts.append(wrap_xml("readonly_files", files_xml))

    if editable_text_files:
        files_xml = format_file_section(editable_text_files)
        context_parts.append(wrap_xml("editable_files", files_xml))

    # Add platform info if provided
    if platform_info:
        context_parts.append(wrap_xml("platform_info", platform_info))

    # Combine all context with proper nesting
    context = "".join(context_parts) if context_parts else "\n"

    # Format task examples if provided
    task_examples_section = format_task_examples(task_examples)

    context_content = (
        f"{wrap_xml('context', context)}\n"
        + wrap_xml("task_instructions", task_instructions)
        + f"{task_examples_section}"
    )

    messages = [{"role": "system", "content": system_prompt}]

    if done_messages:
        messages.extend(done_messages)

    if cur_messages:
        messages.extend(cur_messages[:-1])
        final_user_content = cur_messages[-1]["content"]
    else:
        final_user_content = ""

    final_user_message = {
        "role": "user",
        "content": context_content + "\n\n" + final_user_content,
    }

    messages.append(final_user_message)

    return messages
