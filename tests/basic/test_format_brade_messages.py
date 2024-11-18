# This file uses the Brade coding style: full modern type hints and strong documentation.
# Expect to resolve merges manually. See CONTRIBUTING.md.

"""Unit tests for format_brade_messages function."""

import pytest

from aider.coders.format_brade_messages import REST_OF_MESSAGE_IS_FROM_APP, FileContent
from aider.coders.types import ChatMessage


@pytest.fixture
def sample_done_messages() -> list[ChatMessage]:
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
def sample_cur_messages() -> list[ChatMessage]:
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


def test_basic_message_structure(
    sample_done_messages: list[ChatMessage], sample_cur_messages: list[ChatMessage]
) -> None:
    """Tests that format_brade_messages returns correctly structured message list.

    Validates:
    - Message sequence follows required structure
    - XML sections appear in correct order
    - Message content is preserved appropriately
    - Context message contains all required sections
    """
    from aider.coders.format_brade_messages import format_brade_messages

    test_platform = "Test platform info"
    test_repo_map = "Sample repo structure"

    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=sample_done_messages,
        cur_messages=sample_cur_messages,
        repo_map=test_repo_map,
        readonly_text_files=[],
        editable_text_files=[],
        platform_info=test_platform,
    )

    # Verify message sequence structure
    assert isinstance(messages, list)
    assert len(messages) > 0

    # 1. System message must be first
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a helpful AI assistant"

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

    # 4. Final message should contain both user content and context
    final_msg = messages[-1]
    assert final_msg["role"] == "user"
    content = final_msg["content"]

    # Check that user's original message appears first
    assert content.startswith("Final current message")

    # Check that context follows
    assert REST_OF_MESSAGE_IS_FROM_APP in content
    assert "more recent and reliable than anything in earlier chat messages" in content

    # XML sections must appear in correct order
    sections = [
        "<context>",
        "<repository_map>",
        test_repo_map,
        "</repository_map>",
        "<platform_info>",
        test_platform,
        "</platform_info>",
        "</context>",
    ]

    last_pos = -1
    for section in sections:
        pos = content.find(section)
        assert pos != -1, f"Missing section: {section}"
        assert pos > last_pos, f"Out of order section: {section}"
        last_pos = pos


def test_format_task_examples() -> None:
    """Tests the format_task_examples function.

    Validates:
    - Empty string returned for None/empty input
    - Examples are properly transformed into XML format
    - Messages are properly paired and transformed
    - Invalid message pairs are rejected
    """
    from aider.coders.format_brade_messages import format_task_examples

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
    assert "<task_examples>" in result
    assert "</task_examples>" in result
    assert "<example>" in result
    assert "</example>" in result

    # Check message transformation
    assert "<message role='user'>Example request</message>" in result
    assert "<message role='assistant'>Example response</message>" in result

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


def test_task_examples_integration() -> None:
    """Tests integration of format_task_examples with format_brade_messages.

    Validates that task examples are properly included in the final formatted message.
    """
    from aider.coders.format_brade_messages import format_brade_messages

    examples = [
        {"role": "user", "content": "Example request"},
        {"role": "assistant", "content": "Example response"},
    ]

    messages = format_brade_messages(
        system_prompt="Test prompt",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        task_examples=examples,
        readonly_text_files=[],
        editable_text_files=[],
        platform_info="Test platform info",
    )

    final_msg = messages[-1]
    content = final_msg["content"]

    # Check that user's message appears first
    assert content.startswith("Test")

    # Check examples appear in context after user's message
    assert "<task_examples>" in content
    assert "<message role='user'>Example request</message>" in content
    assert "<message role='assistant'>Example response</message>" in content


def test_system_message_handling() -> None:
    """Tests that system messages are properly handled.

    Validates:
    - System message appears first in sequence
    - System message content is preserved exactly
    - System message is separate from task instructions
    - Empty/None system message is handled appropriately
    - System message appears only once
    """
    from aider.coders.format_brade_messages import format_brade_messages

    test_system = "Test system prompt"
    test_instructions = "Test task instructions"

    # Test basic system message handling
    messages = format_brade_messages(
        system_prompt=test_system,
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        task_instructions=test_instructions,
        readonly_text_files=[],
        editable_text_files=[],
    )

    # Verify system message position and uniqueness
    assert len(messages) > 0
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == test_system
    assert all(msg["role"] != "system" for msg in messages[1:])

    # Verify system message is separate from task instructions
    final_msg = messages[-1]
    content = final_msg["content"]
    assert test_system not in content
    assert "<task_instructions>" in content
    assert test_instructions in content

    # Test empty system message
    messages = format_brade_messages(
        system_prompt="",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test"}],
        readonly_text_files=[],
        editable_text_files=[],
    )
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == ""

    # Test None system message
    with pytest.raises(ValueError, match="system_prompt cannot be None"):
        format_brade_messages(
            system_prompt=None,  # type: ignore
            task_instructions="Test task instructions",
            done_messages=[],
            cur_messages=[{"role": "user", "content": "Test"}],
            readonly_text_files=[],
            editable_text_files=[],
        )


def test_task_instructions_handling() -> None:
    """Tests that task instructions are properly included in the final user message.

    Validates:
    - Task instructions appear in <task_instructions> section when provided
    - Section is omitted when no instructions provided
    - Empty string instructions are handled like None
    - Opening text only mentions task_instructions when they are present
    """
    from aider.coders.format_brade_messages import format_brade_messages

    task_instructions = "Test task instructions"
    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        task_instructions=task_instructions,
        readonly_text_files=[],
        editable_text_files=[],
        platform_info="Test platform info",
    )

    final_msg = messages[-1]
    content = final_msg["content"]

    # Verify user's message appears first
    assert content.startswith("Test message")

    # Check task instructions section and opening text
    assert REST_OF_MESSAGE_IS_FROM_APP in content
    assert "<task_instructions>" in content
    assert task_instructions in content

    # Test empty string instructions (should behave like None)
    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        task_instructions="",
        readonly_text_files=[],
        editable_text_files=[],
        platform_info="Test platform info",
    )
    final_msg = messages[-1]
    content = final_msg["content"]
    assert REST_OF_MESSAGE_IS_FROM_APP in content
    assert "<task_instructions>" not in content

    # Check omission when None
    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        task_instructions=None,
        readonly_text_files=[],
        editable_text_files=[],
        platform_info="Test platform info",
    )
    final_msg = messages[-1]
    content = final_msg["content"]
    assert REST_OF_MESSAGE_IS_FROM_APP in content
    assert "<task_instructions>" not in content


def test_file_content_handling(sample_files: list[tuple[str, str]]) -> None:
    """Tests that file content is properly included in the final user message.

    Validates core file handling functionality:
    - Basic readonly_files section structure and content
    - Basic editable_files section structure and content
    - Simple file content preservation
    - Empty/None file list handling
    """
    from aider.coders.format_brade_messages import format_brade_messages

    # Test basic file content structure with minimal files
    test_files = [
        ("test.py", "def test():\n    return True"),  # Simple function
        ("data.txt", "Test content\nLine 2"),  # Simple text file
    ]

    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map="",
        readonly_text_files=[test_files[0]],  # test.py as readonly
        editable_text_files=[test_files[1]],  # data.txt as editable
        platform_info="Test platform info",
    )

    final_msg = messages[-1]
    content = final_msg["content"]

    # Verify user's message appears first
    assert content.startswith("Test message")

    # Verify readonly files section
    assert "<readonly_files>" in content
    assert "<file path='test.py'>" in content
    assert "def test():" in content
    assert "return True" in content
    assert "</readonly_files>" in content

    # Verify editable files section
    assert "<editable_files>" in content
    assert "<file path='data.txt'>" in content
    assert "Test content" in content
    assert "Line 2" in content
    assert "</editable_files>" in content

    # Test empty file lists
    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map="",
        readonly_text_files=[],
        editable_text_files=[],
        platform_info="Test platform info",
    )
    final_msg = messages[-1]
    content = final_msg["content"]
    assert "<readonly_files>" not in content
    assert "<editable_files>" not in content

    # Test None for file lists
    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map="",
        readonly_text_files=None,
        editable_text_files=None,
        platform_info="Test platform info",
    )
    final_msg = messages[-1]
    content = final_msg["content"]
    assert "<readonly_files>" not in content
    assert "<editable_files>" not in content


def test_platform_info_handling() -> None:
    """Tests that platform info is properly included in the final user message.

    Validates:
    - Platform info appears in <platform_info> section when provided
    - Section is omitted when no platform info is provided
    """
    from aider.coders.format_brade_messages import format_brade_messages

    test_platform = "Test platform info"

    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        platform_info=test_platform,
        readonly_text_files=[],
        editable_text_files=[],
    )

    final_msg = messages[-1]
    content = final_msg["content"]

    # Verify user's message appears first
    assert content.startswith("Test message")

    # Check platform info inclusion
    assert "<platform_info>" in content
    assert test_platform in content

    # Check omission when empty
    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        platform_info=None,
        readonly_text_files=[],
        editable_text_files=[],
    )
    final_msg = messages[-1]
    assert "<platform_info>" not in final_msg["content"]


def test_repo_map_handling() -> None:
    """Tests that repository map content is properly included.

    Validates:
    - Repo map appears in <repository_map> section when provided
    - Section is omitted when no repo map is provided
    - XML structure is correct
    - Content is preserved exactly
    - Empty/None inputs are handled correctly
    """
    from aider.coders.format_brade_messages import format_brade_messages

    # Test basic repo map inclusion
    test_map = "Sample repo map content\nwith multiple lines\nand special chars: <>& "

    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map=test_map,
        readonly_text_files=[],
        editable_text_files=[],
    )

    final_msg = messages[-1]
    content = final_msg["content"]

    # Verify user's message appears first
    assert content.startswith("Test message")

    # Check XML structure
    assert "<repository_map>" in content
    assert "</repository_map>" in content

    # Check content preservation
    assert test_map in content

    # Check multiline handling
    assert "with multiple lines" in content
    assert "and special chars: <>& " in content

    # Test empty string input
    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map="",
        readonly_text_files=[],
        editable_text_files=[],
    )
    final_msg = messages[-1]
    assert "<repository_map>" not in final_msg["content"]

    # Test None input
    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map=None,
        readonly_text_files=[],
        editable_text_files=[],
    )
    final_msg = messages[-1]
    assert "<repository_map>" not in final_msg["content"]

    # Test whitespace-only input
    messages = format_brade_messages(
        system_prompt="You are a helpful AI assistant",
        task_instructions="Test task instructions",
        done_messages=[],
        cur_messages=[{"role": "user", "content": "Test message"}],
        repo_map="   \n  \t  ",
        readonly_text_files=[],
        editable_text_files=[],
    )
    final_msg = messages[-1]
    assert "<repository_map>" not in final_msg["content"]


def test_message_combination() -> None:
    """Tests that user messages and context are properly combined.

    Validates:
    - User's message appears first in the combined content
    - Context follows user's message with proper separation
    - All intermediate messages are preserved
    - Message sequence is correct
    """
    from aider.coders.format_brade_messages import format_brade_messages

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

    # Check final combined message
    final_msg = messages[-1]
    content = final_msg["content"]

    # Verify user's message appears first
    assert content.startswith("Final message")

    # Verify context follows with proper separation
    assert REST_OF_MESSAGE_IS_FROM_APP in content

    # Verify context sections are present
    assert "<context>" in content
    assert "<repository_map>" in content
    assert "Test map" in content
    assert "<platform_info>" in content
    assert "Test platform" in content

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

    final_msg = messages[-1]
    content = final_msg["content"]

    # Verify correct handling of single message case
    assert content.startswith("Single message")
    assert REST_OF_MESSAGE_IS_FROM_APP in content
    assert len(messages) == 2  # Just system prompt and combined message
