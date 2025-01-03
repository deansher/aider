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
    - All sections appear in system message
    - Sections appear in correct order
    - User messages remain pure without any sections
    - Content of each section is preserved correctly
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
    )

    system_msg = messages[0]
    assert system_msg["role"] == "system"
    assert system_msg["content"] == system_prompt

    final_user_msg = messages[-1]
    assert final_user_msg["role"] == "user"

    # Check structure of final user message
    final_user_content = final_user_msg["content"]
    sections = [
        "<repository_map>",
        test_repo_map,
        "</repository_map>",
        "<readonly_files>",
        "<file path='test.py'>",
        "print('test')",
        "</readonly_files>",
        "<platform_info>",
        test_platform,
        "</platform_info>",
        "</context>",
        "<task_instructions>",
        test_instructions,
        "</task_instructions>",
        "<task_examples>",
        "Example request",
        "Example response",
        "</task_examples>",
        "Test message",
    ]
    # Start with the last instance of <context> to skip over any mentions of the sections
    # in preface material.
    last_pos = final_user_content.rindex("<context>")
    for section in sections:
        pos = final_user_content.find(section, last_pos)
        assert pos != -1, f"Missing section {section!r} after <context> in:\n{final_user_content}"
        assert (
            pos > last_pos
        ), f"Section {section!r} out of order after <context> in:\n{final_user_content}"
        last_pos = pos


def test_unsupported_context_placement() -> None:
    """Tests that unsupported context placement values raise exceptions."""

    # Test with INITIAL_USER_MESSAGE (not yet supported)
    with pytest.raises(ValueError, match="Only FINAL_USER_MESSAGE placement"):
        format_brade_messages(
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            context_message_placement=PromptElementPlacement.INITIAL_USER_MESSAGE,
        )

    # Test with SYSTEM_MESSAGE (not yet supported)
    with pytest.raises(ValueError, match="Only FINAL_USER_MESSAGE placement"):
        format_brade_messages(
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            context_message_placement=PromptElementPlacement.SYSTEM_MESSAGE,
        )


def test_element_locations() -> None:
    """Tests that elements can be placed in different messages using ElementLocation.
    
    Validates:
    - Elements can be placed independently in different messages
    - New location parameters override old ones when both are present
    - Content appears correctly in specified locations
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
        # Use new location parameters
        context_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
        task_examples_location=ElementLocation(
            placement=PromptElementPlacement.SYSTEM_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
        # Keep task instructions in final user message
        task_instructions_location=ElementLocation(
            placement=PromptElementPlacement.FINAL_USER_MESSAGE,
            position=PromptElementPosition.PREPEND,
        ),
        # Add old parameters to verify they're overridden
        context_message_placement=PromptElementPlacement.FINAL_USER_MESSAGE,
        context_position=PromptElementPosition.PREPEND,
    )

    # Verify system message contains context and examples
    system_msg = messages[0]["content"]
    assert "<context>" in system_msg, "Context should be in system message"
    assert repo_map in system_msg, "Repo map should be in system message"
    assert platform_info in system_msg, "Platform info should be in system message"
    assert "<task_examples>" in system_msg, "Task examples should be in system message"
    assert "Example request" in system_msg, "Example content should be in system message"

    # Verify final user message contains only task instructions
    final_msg = messages[-1]["content"]
    assert "<task_instructions>" in final_msg, "Task instructions should be in final message"
    assert task_instructions in final_msg, "Task instructions content should be in final message"
    assert "<context>" not in final_msg, "Context should not be in final message"
    assert "<task_examples>" not in final_msg, "Task examples should not be in final message"
    """Tests that unsupported context position values raise exceptions."""

    # Test with INSERT (not yet supported)
    with pytest.raises(ValueError, match="Only PREPEND position"):
        format_brade_messages(
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            context_position=PromptElementPosition.APPEND,
        )


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
    assert "<task_examples>" in result, f"Expected task_examples tag in:\n{result}"
    assert "</task_examples>" in result, f"Expected closing task_examples tag in:\n{result}"
    assert "<example>" in result, f"Expected example tag in:\n{result}"
    assert "</example>" in result, f"Expected closing example tag in:\n{result}"

    # Check message transformation
    assert (
        "<message role='user'>Example request</message>" in result
    ), f"Expected user message in:\n{result}"
    assert (
        "<message role='assistant'>Example response</message>" in result
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


def test_wrap_xml() -> None:
    """Tests that wrap_xml correctly handles empty, whitespace, and non-empty content.

    Validates:
    - Empty string content results in no trailing newline
    - None content results in no trailing newline
    - Whitespace-only content results in no trailing newline
    - Non-empty content gets exactly one trailing newline
    - Opening/closing tags and their newlines are consistent
    """
    from aider.brade_prompts import wrap_xml

    # Test empty string
    result = wrap_xml("test", "")
    assert result == "<test>\n</test>\n"

    # Test None
    result = wrap_xml("test", None)
    assert result == "<test>\n</test>\n"

    # Test whitespace-only strings
    result = wrap_xml("test", "   ")
    assert result == "<test>\n</test>\n"
    result = wrap_xml("test", "\n")
    assert result == "<test>\n</test>\n"
    result = wrap_xml("test", "\t  \n  ")
    assert result == "<test>\n</test>\n"

    # Test non-empty content
    result = wrap_xml("test", "content")
    assert result == "<test>\ncontent\n</test>\n", f"Unexpected result: {result}"
    result = wrap_xml("test", "line1\nline2")
    assert result == "<test>\nline1\nline2\n</test>\n", f"Unexpected result: {result}"

    # Test mixed content and whitespace
    result = wrap_xml("test", "content  \n  ")
    assert result == "<test>\ncontent  \n  \n</test>\n", f"Unexpected result: {result}"
    result = wrap_xml("test", "  \ncontent\n  ")
    assert result == "<test>\n  \ncontent\n  \n</test>\n", f"Unexpected result: {result}"
    result = wrap_xml("test", "\n  content  \n")
    assert result == "<test>\n\n  content  \n</test>\n", f"Unexpected result: {result}"


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

    # Test empty file lists
    messages = format_brade_messages(
        system_prompt="Test prompt",
        task_instructions="Test instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        readonly_text_files=[],
        editable_text_files=[],
    )
    final_content = messages[-1]["content"]
    assert "<readonly_files>" not in final_content
    assert "<editable_files>" not in final_content

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
    )
    final_content = messages[-1]["content"]
    assert "<readonly_files>" in final_content
    assert "<file path='test.py'>" in final_content
    assert "<file path='data.txt'>" in final_content
    assert "def test():" in final_content
    assert "Sample data" in final_content

    # Test error handling for malformed tuples
    with pytest.raises(ValueError):
        format_brade_messages(
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            readonly_text_files=[("test.py",)],  # Missing content
        )

    with pytest.raises(ValueError):
        format_brade_messages(
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            readonly_text_files=[("test.py", "content", "extra")],  # Extra element
        )

    with pytest.raises(ValueError):
        format_brade_messages(
            system_prompt="Test prompt",
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            readonly_text_files=[(42, "content")],  # Wrong type for filename
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
    )
    final_content = messages[-1]["content"]
    assert "<platform_info>" in final_content
    assert test_platform in final_content
    assert "</platform_info>" in final_content

    # Test without platform info
    messages = format_brade_messages(
        system_prompt="Test prompt",
        task_instructions="Test instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        platform_info=None,
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
    from aider.brade_prompts import format_brade_messages, wrap_xml

    # Test empty string handling
    assert wrap_xml("test", "") == "<test>\n</test>\n"
    assert wrap_xml("test", None) == "<test>\n</test>\n"

    # Test whitespace-only strings
    assert wrap_xml("test", "   ") == "<test>\n</test>\n"
    assert wrap_xml("test", "\n") == "<test>\n</test>\n"
    assert wrap_xml("test", "\t  \n  ") == "<test>\n</test>\n"

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
    assert "<repository_map>" not in final_content
    assert "<platform_info>" not in final_content
    assert "<readonly_files>" not in final_content
    assert "<editable_files>" not in final_content


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
            system_prompt=None,
            task_instructions="Test instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
        )

    # Test malformed task examples
    with pytest.raises(ValueError):
        format_brade_messages(
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
        format_brade_messages(
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
            readonly_text_files="not a list",  # Should be list of tuples
        )
