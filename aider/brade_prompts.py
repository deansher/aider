# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

"""Functions for formatting chat messages according to Brade's prompt structure.

This module implements Brade's approach to structuring prompts for LLM interactions.
It follows the guidelines in design_docs/anthropic_docs/claude_prompting_guide.md.

# Guidelines for Writing Prompts

When writing or modifying prompts in this module:

1. Clarity and Structure
   - Use clear, concise language
   - Break complex ideas into bullet points or numbered lists
   - Use consistent formatting and indentation
   - Include examples for complex concepts

2. XML Sections
   - Use XML tags to clearly separate different prompt components
   - Maintain consistent tag naming and structure
   - Document the purpose and content of each section

3. Documentation
   - Keep docstrings focused and specific
   - Document key invariants and assumptions
   - Explain the "why" behind complex decisions
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, TypeAlias

from .types import ChatMessage

# Type definitions for prompt formatting
FileContent: TypeAlias = Tuple[str, str]  # (filename, content)


class PromptElementPlacement(Enum):
    """Controls which message gets a prompt element, such as a context or task element.

    Values:
        FINAL_USER_MESSAGE: Add element to the final user message.
        INITIAL_USER_MESSAGE: Add element to the first user message.
            This option is not yet supported.
        SYSTEM_MESSAGE: Add element to the system message.
            This option is also not yet supported.
    """

    FINAL_USER_MESSAGE = "final_user_message"
    INITIAL_USER_MESSAGE = "initial_user_message"
    SYSTEM_MESSAGE = "system_message"


class PromptElementPosition(Enum):
    """Controls where a prompt element, such as a context or task element, is placed in the message.

    Values:
        PREPEND: Add element at the start of the message.
            This is currently the only supported option.
        APPEND: Add element at the end of the message.
            This option is not yet supported.
    """

    PREPEND = "prepend"
    APPEND = "append"


CONTEXT_SECTION = "<brade:context>...</brade:context>"

PROJECT_CONTEXT_SECTION = "<brade:project_context>...</brade:project_context>"
REPO_MAP_SECTION = "<brade:repository_map>...</brade:repository_map>"
EDITABLE_FILES_SECTION = "<brade:editable_files>...</brade:editable_files>"
READONLY_FILES_SECTION = "<brade:readonly_files>...</brade:readonly_files>"

ENVIRONMENT_CONTEXT_SECTION = (
    "<brade:environment_context>...</brade:environment_context>"
)

TASK_INSTRUCTIONS_SECTION = "<brade:task_instructions>...</brade:task_instructions>"
TASK_EXAMPLES_SECTION = "<brade:task_examples>...</brade:task_examples>"

BRADE_PERSONA_PROMPT = f"""You are Brade, a highly skilled and experienced AI software engineer.
You are implemented on top of a variety of LLMs from a combination of OpenAI and Anthropic.
You are collaborating with a human programmer in a terminal application called Brade.

# How You Collaborate with Your Partner

When you speak in this chat, you should assume that you are speaking to your human partner.

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

# How You Work with Your Partner

You work methodically and collaboratively:

1. Understand the Context
   - Review task instructions and examples
   - Study the repository structure
   - Examine relevant files
   - Consider platform details
   - Learn from conversation history

2. Communicate Clearly
   - Ask questions when needed
   - Share your analysis
   - Make specific proposals
   - Explain your reasoning
   - Seek partner feedback

3. Focus on Quality
   - Write clean, maintainable code
   - Make changes systematic and clear
   - Review work thoroughly
   - Address important issues promptly
   - Defer non-critical improvements

# Context and Task Information

The Brade Applicatiom provides you with the following information, which is not seen by the user:

- {CONTEXT_SECTION} Contains the repo map, file contents, platform info, etc.
  This is the latest information at this point in the chat. In particular, file contents shown in the <context> section 
  (in <readonly_files> or <editable_files>) are the latest project file versions at this point in the chat, superceding
  any other file content shown in chat messages.
- {TASK_INSTRUCTIONS_SECTION}: Contains the requirements, constraints, and guidance for the current task.
- {TASK_EXAMPLES_SECTION}: Contains example conversations that demonstrate how to carry out the task.

```
"""

THIS_MESSAGE_IS_FROM_APP = """This message is from the Brade application, rather than from your partner.
Your partner does not see this message.

"""

REST_OF_MESSAGE_IS_FROM_APP = """(The rest of this message is from the Brade application, rather than from your partner.
Your partner does not see this portion of the message.)

"""


def format_task_examples(task_examples: list[dict[str, str]] | None) -> str:
    """Formats task example messages into XML structure.

    This function validates and transforms example conversations into XML format,
    showing paired user/assistant interactions that demonstrate desired behavior.

    Args:
        task_examples: List of message dictionaries containing example conversations.
            Messages must be in pairs (user, assistant) demonstrating desired behavior.
            Can be None to indicate no examples.
            Each message must be a dict with 'role' and 'content' string fields.

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
            raise ValueError(
                "task_examples must alternate between user and assistant messages"
            )

        examples_xml += (
            "<brade:example>\n"
            f"<brade:message role='user'>{user_msg['content']}</brade:message>\n"
            f"<brade:message role='assistant'>{asst_msg['content']}</brade:message>\n"
            "</brade:example>\n"
        )

    return wrap_brade_xml("task_examples", examples_xml)


def wrap_brade_xml(tag: str, content: str | None) -> str:
    """Wraps content in XML tags with the 'brade' namespace, always including tags even for empty content.

    The function ensures consistent newline handling:
    - A newline after the opening tag
    - For non-empty content: exactly one newline at the end of the content
    - For empty/whitespace content: no additinal newline, so the opening and closing tags
      are on adjacent lines
    - A newline after the closing tag

    Args:
        tag: The XML tag name to use (will be prefixed with 'brade:')
        content: The content to wrap, can be None/empty

    Returns:
        The wrapped content with namespaced tags, containing empty string if content is None/empty
    """
    if not content:
        content = ""

    # Handle whitespace-only content
    if not content.strip():
        return f"<brade:{tag}>\n</brade:{tag}>\n"

    stripped_content = content.rstrip("\n")
    return f"<brade:{tag}>\n{stripped_content}\n</brade:{tag}>\n"


def format_file_section(files: list[FileContent] | None) -> str:
    """Formats a list of files and their contents into an XML section.

    Always returns a properly formatted XML section, even when files is None or empty.
    This maintains consistent structure and makes it clear when a section exists but
    is empty.

    Args:
        files: List of FileContent tuples, each containing:
            - filename (str): The path/name of the file
            - content (str): The file's content
            Can be None to indicate no files.

    Returns:
        XML formatted string containing the files and their contents, or an empty
        section if no files are provided.

    Raises:
        TypeError: If files is not None and not a list of FileContent tuples
        ValueError: If any tuple in files doesn't have exactly 2 string elements
    """
    if files is None:
        return "\n"  # Empty but valid section content

    if not isinstance(files, list):
        raise TypeError("files must be None or a list of (filename, content) tuples")

    if not files:
        return "\n"  # Empty but valid section content

    result = ""
    for item in files:
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("Each item in files must be a (filename, content) tuple")

        fname, content = item
        if not isinstance(fname, str) or not isinstance(content, str):
            raise ValueError("Filename and content must both be strings")

        result += f"<brade:file path='{fname}'>\n{content}\n</brade:file>\n"
    return result


@dataclass(frozen=True)
class ElementLocation:
    """Specifies where to place a prompt element in the message sequence.

    Attributes:
        placement: Which message receives the element
        position: Where in the message the element appears
    """

    placement: PromptElementPlacement
    position: PromptElementPosition


@dataclass
class MessageElement:
    """A message element to be placed in a specific location.

    Attributes:
        content: The element's content as a string
        location: Where to place the element in the message sequence
    """

    content: str
    location: ElementLocation


def format_brade_messages(
    system_prompt: str,
    task_instructions: str,
    done_messages: list[dict[str, str]],
    cur_messages: list[dict[str, str]],
    repo_map: str | None = None,
    readonly_text_files: list[FileContent] | None = None,
    editable_text_files: list[FileContent] | None = None,
    image_files: list[FileContent] | None = None,
    platform_info: str | None = None,
    task_examples: list[dict[str, str]] | None = None,
    task_instructions_reminder: str | None = None,
    context_location: ElementLocation | None = None,
    task_instructions_location: ElementLocation | None = None,
    task_examples_location: ElementLocation | None = None,
    task_instructions_reminder_location: ElementLocation | None = None,
) -> list[dict[str, str]]:
    """Formats chat messages according to Brade's prompt structure.

    This function implements Brade's approach to structuring prompts for LLM interactions.
    It organizes context into distinct sections to support clear decision-making:

    Project Context:
    - Repository structure and content
    - File contents and permissions
    - Reference in responses using <project_context>

    Environment Context:
    - Platform and runtime information
    - Reference in responses using <environment_context>

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
        task_instructions_reminder: Optional reminder text to be included in the prompt.
            This is typically used for system-level reminders about task requirements
            or constraints that should be kept separate from the main task instructions.
        task_instructions_reminder_location: Optional ElementLocation specifying where
            to place the reminder in the message sequence. Follows the same placement
            rules as other elements.

    Returns:
        The formatted sequence of messages ready for the LLM

    Raises:
        ValueError: If system_prompt is None or if task_examples are malformed
        TypeError: If file content tuples are not properly formatted
    """
    if system_prompt is None:
        raise ValueError("system_prompt cannot be None")

    for _loc_label, loc in [
        ("context_location", context_location),
        ("task_instructions_location", task_instructions_location),
        ("task_examples_location", task_examples_location),
        ("task_instructions_reminder_location", task_instructions_reminder_location),
    ]:
        if loc is not None:
            if loc.placement == PromptElementPlacement.INITIAL_USER_MESSAGE:
                raise ValueError(
                    "Only FINAL_USER_MESSAGE or SYSTEM_MESSAGE are supported at this time"
                )

    # Build the context sections

    # Build project context
    project_parts = []
    if repo_map and repo_map.strip():
        project_parts.append(wrap_brade_xml("repository_map", repo_map))
    # Always include file sections, even when empty
    files_xml = format_file_section(readonly_text_files)
    project_parts.append(wrap_brade_xml("readonly_files", files_xml))
    files_xml = format_file_section(editable_text_files)
    project_parts.append(wrap_brade_xml("editable_files", files_xml))
    project_context = wrap_brade_xml(
        "project_context", "".join(project_parts)
    )

    # Build environment context
    environment_context = wrap_brade_xml(
        "environment_context", platform_info if platform_info else "\n"
    )

    # Add guidance about using context
    context_preface = f"""<!--
This material is generated by the Brade Application and is not seen by the user.
-->

How to Use Context Sections:

1. Project Context (${PROJECT_CONTEXT_SECTION}):
   - ${REPO_MAP_SECTION}: provides an overview of repository structure and content, 
     with file snippets.
   - ${EDITABLE_FILES_SECTION}: shows complete latest content of files you are likely to edit.
   - ${READONLY_FILES_SECTION}: displays latest content of files provided for reference, although
     you can also choose to edit these if they are inside the project.
   - Latest file contents here supersede any content in chat history.

2. Environment Context (${ENVIRONMENT_CONTEXT_SECTION}):
   - Platform and runtime details
   - Use when suggesting commands or platform-specific code

These file contents and repo details are the latest versions at this point in the chat,
superceding any other file content shown in chat messages.

"""

    # Combine all context sections
    context_str = wrap_brade_xml(
        "context", f"{context_preface}{project_context}{environment_context}"
    )

    # Format task examples if provided
    task_examples_section = format_task_examples(task_examples)
    if task_examples_section.strip():
        task_examples_comment = (
            "<!-- This material is generated by the Brade Application and is not"
            " seen by the user. -->\n"
        )
        task_examples_section = task_examples_comment + task_examples_section

    instructions_preface = (
        f"<!-- This material is generated by the Brade Application and"
        " is not seen by the user. -->\n"
        f"Examples of how to carry out this task are provided in {TASK_EXAMPLES_SECTION}.\n\n"
    )
    instructions_str = wrap_brade_xml(
        "task_instructions", f"{instructions_preface}{task_instructions}"
    )

    # Create message elements with their locations
    elements: list[MessageElement] = []
    if context_location:
        elements.append(MessageElement(context_str, context_location))
    if task_instructions_location:
        elements.append(MessageElement(instructions_str, task_instructions_location))
    if task_examples_location:
        elements.append(MessageElement(task_examples_section, task_examples_location))

    if task_instructions_reminder_location and task_instructions_reminder:
        reminder_str = wrap_brade_xml(
            "task_instructions_reminder",
            "<!-- The Brade application always automatically inserts this reminder. -->\n"
            + task_instructions_reminder,
        )
        elements.append(
            MessageElement(reminder_str, task_instructions_reminder_location)
        )

    # messages array always starts with the system message
    messages = [{"role": "system", "content": system_prompt}]

    if done_messages:
        messages.extend(done_messages)

    # Add elements to system message if requested
    system_elements = [
        elem
        for elem in elements
        if elem.location.placement == PromptElementPlacement.SYSTEM_MESSAGE
    ]
    for elem in system_elements:
        if elem.location.position == PromptElementPosition.PREPEND:
            messages[0]["content"] = elem.content + messages[0]["content"]
        else:  # APPEND
            messages[0]["content"] += elem.content

    # Prepare the final user message
    final_user_content = ""
    if cur_messages:
        # We put everything except the last message unchanged
        messages.extend(cur_messages[:-1])
        final_user_content = cur_messages[-1]["content"]

    # Build the final message content in three phases:
    # 1. All PREPEND elements
    # 2. User message
    # 3. All APPEND elements

    final_elements = [
        elem
        for elem in elements
        if elem.location.placement == PromptElementPlacement.FINAL_USER_MESSAGE
    ]

    # Phase 1: PREPEND elements
    prepend_elements = [
        elem
        for elem in final_elements
        if elem.location.position == PromptElementPosition.PREPEND
    ]
    prepend_content = ""
    for elem in prepend_elements:
        # Each prepend element goes before any user text
        if prepend_content:
            prepend_content += "\n\n"
        prepend_content += elem.content

    # Phase 2: User message
    # We explicitly place the user’s message after all PREPEND content
    final_msg_content = prepend_content
    if prepend_content and final_user_content:
        final_msg_content += "\n\n"
    final_msg_content += final_user_content

    # Phase 3: APPEND elements
    append_elements = [
        elem
        for elem in final_elements
        if elem.location.position == PromptElementPosition.APPEND
    ]
    for elem in append_elements:
        final_msg_content += "\n\n" + elem.content

    # Now create the final user message
    final_user_message = {
        "role": "user",
        "content": final_msg_content,
    }
    messages.append(final_user_message)

    return messages
