# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

"""Unit tests for format_brade_messages function."""

import pytest

from aider.brade_prompts import (
    ElementLocation,
    PromptElementPlacement,
    PromptElementPosition,
    FileContent,
    format_brade_messages,
    format_task_examples,
    wrap_brade_xml,
)
from aider.types import ChatMessage


@pytest.fixture
def sample_done_messages() -> list[dict[str, str]]:
    """Provides sample conversation history messages.

    This fixture provides messages that represent previous completed exchanges.
    Used as the done_messages parameter in format_brade_messages().

    Returns:
        A list containing historical user and assistant messages.
    """
    return [
        {"role": "user", "content": "Previous message"},
        {"role": "assistant", "content": "Previous response"},
    ]


@pytest.fixture
def sample_cur_messages() -> list[dict[str, str]]:
    """Provides sample current conversation messages.

    This fixture provides messages for the active exchange.
    Used as the cur_messages parameter in format_brade_messages().
    Includes multiple messages to test preservation of intermediate messages.

    Returns:
        A list containing user and assistant messages, ending with a user message.
    """
    return [
        {"role": "user", "content": "First current message"},
        {"role": "assistant", "content": "Intermediate response"},
        {"role": "user", "content": "Final current message"},
    ]


@pytest.fixture
def sample_files() -> list[FileContent]:
    """Provides sample file content for testing.

    Returns:
        List of FileContent tuples for testing file handling.
    """
    return [
        ("test.py", "def test():\n    pass\n"),
        ("data.txt", "Sample data\n"),
    ]


def test_context_and_task_placement() -> None:
    """Tests that <context>, <task_instructions>, and <task_examples> are properly placed.

    Validates:
    - All sections appear in system message when placed there
    - Sections appear in correct order
    - User messages remain pure without any sections when not placed there
    - Content of each section is preserved correctly
    - None locations result in no placement
    """
    system_prompt = "You are a helpful AI assistant"

    test_platform = "Test platform info"
    test_repo_map = "Sample repo structure"
    test_file = ("test.py", "print('test')")
    test_instructions = "Test task instructions"
    test_examples = [
        {"role": "user", "content": "Example request"},
        {"role": "assistant", "content": "Example response"},
    ]

    # Test with explicit system message placement
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=test_instructions,
        task_examples=test_examples,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map=test_repo_map,
        readonly_text_files=[test_file],
        editable_text_files=[],
        platform_info=test_platform,
        context_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        task_instructions_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        task_examples_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
    )

    system_msg = messages[0]
    assert system_msg["role"] == "system"
    
    # Check structure of system message
    system_content = system_msg["content"]
    sections = [
        system_prompt,
        "<brade:context>",
        "<brade:project_context>",
        "<brade:repository_map>",
        test_repo_map,
        "</brade:repository_map>",
        "<brade:readonly_files>",
        "<brade:file path='test.py'>",
        "print('test')",
        "</brade:file>",
        "</brade:readonly_files>",
        "</brade:project_context>",
        "<brade:environment_context>",
        test_platform,
        "</brade:environment_context>",
        "</brade:context>",
        "<brade:task_instructions>",
        test_instructions,
        "</brade:task_instructions>",
        "<brade:task_examples>",
        "Example request",
        "Example response",
        "</brade:task_examples>",
    ]
    
    last_pos = 0
    for section in sections:
        pos = system_content.find(section, last_pos)
        assert pos != -1, f"Missing section {section!r} in system message:\n{system_content}"
        assert pos >= last_pos, f"Section {section!r} out of order in system message:\n{system_content}"
        last_pos = pos

    # Verify user message is clean
    final_user_msg = messages[-1]
    assert final_user_msg["role"] == "user"
    assert final_user_msg["content"] == "Test message"

    # Test with None locations - sections should not appear
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=test_instructions,
        task_examples=test_examples,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map=test_repo_map,
        readonly_text_files=[test_file],
        editable_text_files=[],
        platform_info=test_platform,
        context_location=None,
        task_instructions_location=None,
        task_examples_location=None,
    )

    system_msg = messages[0]
    assert system_msg["role"] == "system"
    assert system_msg["content"] == system_prompt

    final_user_msg = messages[-1]
    assert final_user_msg["role"] == "user"
    assert final_user_msg["content"] == "Test message"


def test_unsupported_context_placement() -> None:
    """Tests that unsupported context placement values raise exceptions."""

    # Test with INITIAL_USER_MESSAGE (not yet supported)
    with pytest.raises(ValueError, match="Only FINAL_USER_MESSAGE or SYSTEM_MESSAGE are supported at this time"):
        format_brade_messages(
            system_prompt="Test system prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            context_location=ElementLocation(
                placement=PromptElementPlacement.INITIAL_USER_MESSAGE,
                position=PromptElementPosition.PREPEND,
            ),
        )


def test_element_locations() -> None:
    """Tests that elements can be placed in different messages using ElementLocation.

    Validates:
    - Elements can be placed independently in different messages
    - Content appears correctly in specified locations
    - None locations result in no placement
    - Task instructions reminder is handled correctly
    """
    system_prompt = "Test system prompt"
    task_instructions = "Test task instructions"
    task_examples = [
        {"role": "user", "content": "Example request"},
        {"role": "assistant", "content": "Example response"},
    ]
    repo_map = "Test repo map"
    platform_info = "Test platform"

    # Test moving context and examples to system message
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=task_instructions,
        task_examples=task_examples,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map=repo_map,
        platform_info=platform_info,
        # Place elements in system message
        context_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
        task_examples_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
        task_instructions_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
    )

    # Verify system message contains all elements
    system_msg = messages[0]["content"]
    assert "<brade:context>" in system_msg, "Context should be in system message"
    assert repo_map in system_msg, "Repo map should be in system message"
    assert platform_info in system_msg, "Platform info should be in system message"
    assert "<brade:task_examples>" in system_msg, "Task examples should be in system message"
    assert "Example request" in system_msg, "Example content should be in system message"
    assert "<brade:task_instructions>" in system_msg, "Task instructions should be in system message"

    # Verify user message is clean
    final_msg = messages[-1]["content"]
    assert final_msg == "Test message", "User message should be clean"

    # Test with None locations - elements should not appear
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=task_instructions,
        task_examples=task_examples,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map=repo_map,
        platform_info=platform_info,
        context_location=None,
        task_examples_location=None,
        task_instructions_location=None,
    )

    # Verify system message is clean
    system_msg = messages[0]["content"]
    assert system_msg == system_prompt, "System message should be clean"

    # Verify user message is clean
    final_msg = messages[-1]["content"]
    assert final_msg == "Test message", "User message should be clean"


def test_task_instructions_reminder_placement() -> None:
    """Tests that task instructions reminder is properly placed.

    Validates:
    - Reminder appears in specified message
    - Reminder appears in correct position
    - Reminder is wrapped in correct XML tags
    - Empty/None reminder is handled correctly
    - None location results in no placement
    """
    system_prompt = "Test system prompt"
    task_instructions = "Test task instructions"
    task_instructions_reminder = "Test reminder"

    # Test with reminder in system message
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=task_instructions,
        task_instructions_reminder=task_instructions_reminder,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        task_instructions_reminder_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        context_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        task_instructions_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
    )

    # Verify reminder appears in system message
    system_msg = messages[0]["content"]
    assert "<brade:task_instructions_reminder>" in system_msg
    assert task_instructions_reminder in system_msg

    # Test with reminder in final user message
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=task_instructions,
        task_instructions_reminder=task_instructions_reminder,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        task_instructions_reminder_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
        context_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
        task_instructions_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
    )

    # Verify reminder appears in final user message
    final_msg = messages[-1]["content"]
    assert "<brade:task_instructions_reminder>" in final_msg
    assert task_instructions_reminder in final_msg

    # Test with None reminder
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=task_instructions,
        task_instructions_reminder=None,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        task_instructions_reminder_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        context_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        task_instructions_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
    )

    # Verify no reminder tags appear
    system_msg = messages[0]["content"]
    assert "<task_instructions_reminder>" not in system_msg

    # Test with None location - reminder should not appear
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=task_instructions,
        task_instructions_reminder=task_instructions_reminder,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        task_instructions_reminder_location=None,
        context_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        task_instructions_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
    )

    # Verify reminder does not appear in any message
    system_msg = messages[0]["content"]
    assert "<task_instructions_reminder>" not in system_msg
    final_msg = messages[-1]["content"]
    assert "<task_instructions_reminder>" not in final_msg


def test_append_positions() -> None:
    """Tests that elements can be appended to messages.

    Validates:
    - Elements can be appended to system messages
    - Elements can be appended to final user messages
    - Mixed prepend/append scenarios work correctly
    """
    system_prompt = "Test system prompt"
    task_instructions = "Test task instructions"
    task_examples = [
        {"role": "user", "content": "Example request"},
        {"role": "assistant", "content": "Example response"},
    ]
    repo_map = "Test repo map"
    platform_info = "Test platform"

    # Test appending to system message
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=task_instructions,
        task_examples=task_examples,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map=repo_map,
        platform_info=platform_info,
        # Move context to system message and append it
        context_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
    )

    # Verify system message has context appended
    system_msg = messages[0]["content"]
    assert system_msg.startswith(system_prompt), "System prompt should come first"
    assert "<brade:context>" in system_msg, "Context should be in system message"
    assert repo_map in system_msg, "Repo map should be in system message"
    assert platform_info in system_msg, "Platform info should be in system message"

    # Test appending to final user message
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=task_instructions,
        task_examples=task_examples,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map=repo_map,
        platform_info=platform_info,
        # Append all elements to final user message
        context_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        task_instructions_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        task_examples_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
    )

    # Verify final user message has context appended
    final_msg = messages[-1]["content"]
    assert final_msg.startswith("Test message"), "User message should come first"
    assert "<brade:context>" in final_msg, "Context should be in final message"
    assert repo_map in final_msg, "Repo map should be in final message"
    assert platform_info in final_msg, "Platform info should be in final message"

    # Test mixed prepend/append scenario
    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions=task_instructions,
        task_examples=task_examples,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map=repo_map,
        platform_info=platform_info,
        # Mix of prepend and append in different messages
        context_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        task_instructions_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
        task_examples_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.APPEND,
        ),
        task_instructions_reminder_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
    )

    # Verify system message
    system_msg = messages[0]["content"]
    assert system_msg.startswith(system_prompt), "System prompt should come first"
    assert "<brade:context>" in system_msg, "Context should be in system message"

    # Verify final user message
    final_msg = messages[-1]["content"]
    assert "<brade:task_instructions>" in final_msg, "Task instructions should be in final message"
    assert "Test message" in final_msg, "User message should be in final message"
    assert "<brade:task_examples>" in final_msg, "Task examples should be in final message"
    # Check order by finding tags at start of lines
    import re
    task_instr_match = re.search(r'^\s*<brade:task_instructions>\s*$', final_msg, re.MULTILINE)
    assert task_instr_match is not None, "Could not find <task_instructions> tag in:\n" + final_msg
    task_instr_pos = task_instr_match.start()

    user_msg_pos = final_msg.find("Test message")
    assert user_msg_pos != -1, "Could not find user message in:\n" + final_msg

    task_ex_match = re.search(r'^\s*<brade:task_examples>\s*$', final_msg, re.MULTILINE)
    assert task_ex_match is not None, "Could not find <task_examples> tag in:\n" + final_msg
    task_ex_pos = task_ex_match.start()

    assert task_instr_pos < user_msg_pos < task_ex_pos, "Elements should be in correct order. Got this:\n" + final_msg


def test_basic_message_structure(
    sample_done_messages: list[dict[str, str]], sample_cur_messages: list[dict[str, str]]
) -> None:
    """Tests that format_brade_messages returns correctly structured message list.

    Validates:
    - Message sequence follows required structure
    - Message content is preserved appropriately
    - Basic system message content
    """
    from aider.brade_prompts import format_brade_messages

    system_prompt = "You are a helpful AI assistant"

    messages = format_brade_messages(
        system_prompt=system_prompt,
        task_instructions="Test task instructions",
        done_messages=sample_done_messages,
        cur_messages=sample_cur_messages,
        repo_map=None,
        readonly_text_files=[],
        editable_text_files=[],
        platform_info=None,
    )

    # Verify message sequence structure
    assert isinstance(messages, list)
    assert len(messages) > 0

    # 1. System message must be first
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == system_prompt

    # 2. Done messages must follow system message exactly
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Previous message"
    assert messages[2]["role"] == "assistant"
    assert messages[2]["content"] == "Previous response"

    # 3. Current messages before final must be preserved exactly
    assert messages[3]["role"] == "user"
    assert messages[3]["content"] == "First current message"
    assert messages[4]["role"] == "assistant"
    assert messages[4]["content"] == "Intermediate response"

    # 4. Final current message must include user content. (It has other stuff.)
    final_msg = messages[-1]
    assert final_msg["role"] == "user"
    assert "Final current message" in final_msg["content"]


def test_format_task_examples() -> None:
    """Tests the format_task_examples function.

    Validates:
    - Empty string returned for None/empty input
    - Examples are properly transformed into XML format
    - Messages are properly paired and transformed
    - Invalid message pairs are rejected
    """
    from aider.brade_prompts import format_task_examples

    # Test None input
    assert format_task_examples(None) == ""

    # Test empty list
    assert format_task_examples([]) == ""

    # Test valid example messages
    examples = [
        {"role": "user", "content": "Example request"},
        {"role": "assistant", "content": "Example response"},
        {"role": "user", "content": "Another request"},
        {"role": "assistant", "content": "Another response"},
    ]

    result = format_task_examples(examples)

    # Check XML structure
    assert "<brade:task_examples>" in result, f"Expected task_examples tag in:\n{result}"
    assert "</brade:task_examples>" in result, f"Expected closing task_examples tag in:\n{result}"
    assert "<brade:example>" in result, f"Expected example tag in:\n{result}"
    assert "</brade:example>" in result, f"Expected closing example tag in:\n{result}"

    # Check message transformation
    assert (
        "<brade:message role='user'>Example request</brade:message>" in result
    ), f"Expected user message in:\n{result}"
    assert (
        "<brade:message role='assistant'>Example response</brade:message>" in result
    ), f"Expected assistant message in:\n{result}"

    # Test invalid message pairs
    with pytest.raises(ValueError, match="must alternate between user and assistant"):
        bad_examples = [
            {"role": "user", "content": "Request"},
            {"role": "user", "content": "Wrong role"},
        ]
        format_task_examples(bad_examples)

    # Test odd number of messages
    with pytest.raises(ValueError, match="must contain pairs"):
        odd_examples = examples[:-1]  # Remove last message
        format_task_examples(odd_examples)


def test_wrap_brade_xml() -> None:
    """Tests that wrap_brade_xml correctly handles empty, whitespace, and non-empty content.

    Validates:
    - Empty string content results in no trailing newline
    - None content results in no trailing newline
    - Whitespace-only content results in no trailing newline
    - Non-empty content gets exactly one trailing newline
    - Opening/closing tags and their newlines are consistent
    - Tags use the 'brade' namespace
    """
    from aider.brade_prompts import wrap_brade_xml

    # Test empty string
    result = wrap_brade_xml("test", "")
    assert result == "<brade:test>\n</brade:test>\n"

    # Test None
    result = wrap_brade_xml("test", None)
    assert result == "<brade:test>\n</brade:test>\n"

    # Test whitespace-only strings
    result = wrap_brade_xml("test", "   ")
    assert result == "<brade:test>\n</brade:test>\n"
    result = wrap_brade_xml("test", "\n")
    assert result == "<brade:test>\n</brade:test>\n"
    result = wrap_brade_xml("test", "\t  \n  ")
    assert result == "<brade:test>\n</brade:test>\n"

    # Test non-empty content
    result = wrap_brade_xml("test", "content")
    assert result == "<brade:test>\ncontent\n</brade:test>\n", f"Unexpected result: {result}"
    result = wrap_brade_xml("test", "line1\nline2")
    assert result == "<brade:test>\nline1\nline2\n</brade:test>\n", f"Unexpected result: {result}"

    # Test mixed content and whitespace
    result = wrap_brade_xml("test", "content  \n  ")
    assert result == "<brade:test>\ncontent  \n  \n</brade:test>\n", f"Unexpected result: {result}"
    result = wrap_brade_xml("test", "  \ncontent\n  ")
    assert result == "<brade:test>\n  \ncontent\n  \n</brade:test>\n", f"Unexpected result: {result}"
    result = wrap_brade_xml("test", "\n  content  \n")
    assert result == "<brade:test>\n\n  content  \n</brade:test>\n", f"Unexpected result: {result}"


def test_message_combination() -> None:
    """Tests that user messages and context are properly combined.

    Validates:
    - User's message appears first in the combined content
    - Context follows user's message with proper separation
    - All intermediate messages are preserved
    - Message sequence is correct
    """
    from aider.brade_prompts import format_brade_messages

    # Test with multiple intermediate messages
    cur_messages = [
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "First response"},
        {"role": "user", "content": "Second message"},
        {"role": "assistant", "content": "Second response"},
        {"role": "user", "content": "Final message"},
    ]

    messages = format_brade_messages(
        system_prompt="Test system prompt",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=cur_messages,
        repo_map="Test map",
        readonly_text_files=[],
        editable_text_files=[],
        platform_info="Test platform",
    )

    # Check that intermediate messages are preserved exactly
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "First message"
    assert messages[2]["role"] == "assistant"
    assert messages[2]["content"] == "First response"
    assert messages[3]["role"] == "user"
    assert messages[3]["content"] == "Second message"
    assert messages[4]["role"] == "assistant"
    assert messages[4]["content"] == "Second response"
    assert messages[5]["role"] == "user"
    assert "Final message" in messages[5]["content"]

    # Test with single message
    messages = format_brade_messages(
        system_prompt="Test system prompt",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Single message"}],
        repo_map="Test map",
        platform_info="Test platform",
        readonly_text_files=[],
        editable_text_files=[],
    )

    assert len(messages) == 2  # Just system prompt and combined message

    assert messages[1]["role"] == "user"
    assert "Single message" in messages[1]["content"]


def test_file_section_formatting() -> None:
    """Tests file section formatting and validation.

    Validates:
    - Correct XML structure for file sections
    - Proper handling of empty file lists
    - Error handling for malformed file content tuples
    """
    from aider.brade_prompts import format_brade_messages

    # Test empty file lists - should include empty sections
    messages = format_brade_messages(
        system_prompt="Test prompt",
        task_instructions="Test instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        readonly_text_files=[],
        editable_text_files=[],
        context_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
    )
    final_content = messages[-1]["content"]
    assert "<brade:readonly_files>\n</brade:readonly_files>" in final_content
    assert "<brade:editable_files>\n</brade:editable_files>" in final_content

    # Test valid file content
    test_files = [
        ("test.py", "def test():\n    pass\n"),
        ("data.txt", "Sample data\n"),
    ]
    messages = format_brade_messages(
        system_prompt="Test prompt",
        task_instructions="Test instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        readonly_text_files=test_files,
        context_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
    )
    final_content = messages[-1]["content"]
    assert "<brade:readonly_files>" in final_content
    assert "<brade:file path='test.py'>" in final_content
    assert "<brade:file path='data.txt'>" in final_content
    assert "def test():" in final_content
    assert "Sample data" in final_content

    # Test error handling for malformed tuples
    with pytest.raises(ValueError):
        format_brade_messages(  # type: ignore[arg-type]  # Intentionally testing malformed tuple
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            readonly_text_files=[("test.py",)],  # type: ignore  # Missing content - intentional test case
        )

    with pytest.raises(ValueError):
        format_brade_messages(  # type: ignore[arg-type]  # Intentionally testing malformed tuple
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            readonly_text_files=[("test.py", "content", "extra")],  # type: ignore  # Extra element - intentional test case
        )

    with pytest.raises(ValueError):
        format_brade_messages(  # type: ignore[arg-type]  # Intentionally testing wrong type
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            readonly_text_files=[(42, "content")],  # type: ignore  # Wrong type for filename - intentional test case
        )


def test_platform_info_handling() -> None:
    """Tests platform info formatting and handling.

    Validates:
    - Platform info appears in correct location
    - Empty platform info is handled gracefully
    - Platform info content is preserved correctly
    """
    from aider.brade_prompts import format_brade_messages

    # Test with platform info
    test_platform = "Test platform details\nMultiple lines\nOf information"
    messages = format_brade_messages(
        system_prompt="Test prompt",
        task_instructions="Test instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        platform_info=test_platform,
        context_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
    )
    final_content = messages[-1]["content"]
    assert "<brade:environment_context>" in final_content
    assert test_platform in final_content
    assert "</brade:environment_context>" in final_content

    # Test without platform info
    messages = format_brade_messages(
        system_prompt="Test prompt",
        task_instructions="Test instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        platform_info=None,
        context_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
    )
    final_content = messages[-1]["content"]
    assert "<platform_info>" not in final_content

    # Test with empty platform info
    messages = format_brade_messages(
        system_prompt="Test prompt",
        task_instructions="Test instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        platform_info="",
        context_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
    )
    final_content = messages[-1]["content"]
    assert "<platform_info>" not in final_content


def test_empty_content_handling() -> None:
    """Tests handling of empty and whitespace-only content.

    Validates:
    - Empty strings are handled properly
    - Whitespace-only strings are handled properly
    - None values are handled properly
    """
    from aider.brade_prompts import format_brade_messages, wrap_brade_xml

    # Test empty string handling
    assert wrap_brade_xml("test", "") == "<brade:test>\n</brade:test>\n"
    assert wrap_brade_xml("test", None) == "<brade:test>\n</brade:test>\n"

    # Test whitespace-only strings
    assert wrap_brade_xml("test", "   ") == "<brade:test>\n</brade:test>\n"
    assert wrap_brade_xml("test", "\n") == "<brade:test>\n</brade:test>\n"
    assert wrap_brade_xml("test", "\t  \n  ") == "<brade:test>\n</brade:test>\n"

    # Test empty content in format_brade_messages
    messages = format_brade_messages(
        system_prompt="Test prompt",
        task_instructions="Test instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": ""}],
        repo_map="",
        platform_info="",
        readonly_text_files=[],
        editable_text_files=[],
    )
    final_content = messages[-1]["content"]
    assert "<brade:repository_map>" not in final_content
    assert "<brade:environment_context>" not in final_content
    assert "<brade:readonly_files>" not in final_content
    assert "<brade:editable_files>" not in final_content


def test_malformed_input_errors() -> None:
    """Tests error handling for malformed input.

    Validates proper error handling for:
    - Invalid file content tuples
    - Malformed task examples
    - Missing required parameters
    """
    from aider.brade_prompts import format_brade_messages, format_task_examples

    # Test missing system prompt
    with pytest.raises(ValueError):
        format_brade_messages(
            system_prompt=None,  # type: ignore[arg-type]  # Intentionally testing None system_prompt
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
        )

    # Test malformed task examples
    with pytest.raises(ValueError):
        format_brade_messages(  # type: ignore[list-item]  # Intentionally testing wrong role sequence
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            task_examples=[
                {"role": "user", "content": "Example request"},
                {"role": "user", "content": "Wrong role"},  # Should be assistant
            ],
        )

    # Test odd number of task examples
    with pytest.raises(ValueError):
        format_brade_messages(  # type: ignore[list-item]  # Intentionally testing incomplete pair
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            task_examples=[
                {"role": "user", "content": "Example request"},
                {"role": "assistant", "content": "Example response"},
                {"role": "user", "content": "Unpaired request"},  # Missing response
            ],
        )

    # Test invalid file content type
    with pytest.raises(TypeError):
        format_brade_messages( 
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            # Previously was: readonly_text_files=[("test.py", "content")]
            # Now intentionally pass a non-list to trigger TypeError:
            readonly_text_files=("test.py", "content"),  # type: ignore[arg-type]
        )
