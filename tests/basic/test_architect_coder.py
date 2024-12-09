import unittest
from unittest.mock import MagicMock, patch

from aider.coders.architect_coder import ArchitectCoder, ArchitectExchange
from aider.io import InputOutput
from aider.models import Model


class TestArchitectExchange(unittest.TestCase):
    """Test the ArchitectExchange class that manages architect-editor-reviewer exchanges."""

    def setUp(self):
        self.architect_response = "Here's my proposal for changes..."
        self.exchange = ArchitectExchange(self.architect_response)

    def test_init(self):
        """Test initialization with architect response."""
        self.assertEqual(len(self.exchange.messages), 1)
        self.assertEqual(self.exchange.messages[0]["role"], "assistant")
        self.assertEqual(self.exchange.messages[0]["content"], self.architect_response)

    def test_append_editor_prompt(self):
        """Test appending editor prompts for both plan and non-plan changes."""
        # Test plan changes prompt
        prompt = self.exchange.append_editor_prompt(is_plan_change=True)
        self.assertIn("plan", prompt.lower())
        self.assertEqual(self.exchange.messages[-1]["role"], "user")
        self.assertEqual(self.exchange.messages[-1]["content"], prompt)

        # Test non-plan changes prompt
        exchange2 = ArchitectExchange(self.architect_response)
        prompt = exchange2.append_editor_prompt(is_plan_change=False)
        self.assertNotIn("plan", prompt.lower())
        self.assertEqual(exchange2.messages[-1]["role"], "user")
        self.assertEqual(exchange2.messages[-1]["content"], prompt)

    def test_append_editor_response(self):
        """Test appending editor response."""
        response = "I've implemented the changes..."
        self.exchange.append_editor_response(response)
        self.assertEqual(self.exchange.messages[-1]["role"], "assistant")
        self.assertEqual(self.exchange.messages[-1]["content"], response)

    def test_append_reviewer_prompt(self):
        """Test appending reviewer prompt."""
        prompt = self.exchange.append_reviewer_prompt()
        self.assertEqual(self.exchange.messages[-1]["role"], "user")
        self.assertEqual(self.exchange.messages[-1]["content"], prompt)

    def test_append_reviewer_response(self):
        """Test appending reviewer response."""
        response = "I've reviewed the changes..."
        self.exchange.append_reviewer_response(response)
        self.assertEqual(self.exchange.messages[-1]["role"], "assistant")
        self.assertEqual(self.exchange.messages[-1]["content"], response)

    def test_get_messages(self):
        """Test getting all messages in the exchange."""
        self.exchange.append_editor_prompt(is_plan_change=False)
        self.exchange.append_editor_response("Changes made")
        messages = self.exchange.get_messages()
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["content"], self.architect_response)

    def test_has_editor_response(self):
        """Test checking for editor response."""
        self.assertFalse(self.exchange.has_editor_response())
        
        self.exchange.append_editor_prompt(is_plan_change=False)
        self.assertFalse(self.exchange.has_editor_response())
        
        self.exchange.append_editor_response("Changes made")
        self.assertTrue(self.exchange.has_editor_response())


class TestArchitectCoder(unittest.TestCase):
    """Test the ArchitectCoder class that coordinates architecture decisions."""

    def setUp(self):
        self.model = Model("gpt-3.5-turbo")
        self.io = InputOutput()
        self.coder = ArchitectCoder.create(self.model, "architect", io=self.io)

    def test_create_coder(self):
        """Test creating subordinate coders."""
        editor = self.coder.create_coder("diff")
        self.assertEqual(editor.edit_format, "diff")
        self.assertFalse(editor.suggest_shell_commands)
        
        reviewer = self.coder.create_coder("ask")
        self.assertEqual(reviewer.edit_format, "ask")
        self.assertFalse(reviewer.suggest_shell_commands)

    def test_process_architect_change_proposal(self):
        """Test processing architect's change proposal."""
        exchange = ArchitectExchange("Here's my proposal...")
        
        # Mock user declining changes
        self.io.confirm_ask = MagicMock(return_value=False)
        self.coder.process_architect_change_proposal(exchange, is_plan_change=False)
        self.assertEqual(len(self.coder.cur_messages), 0)  # No messages recorded
        
        # Mock user accepting changes
        self.io.confirm_ask = MagicMock(return_value=True)
        self.coder.execute_changes = MagicMock()
        self.coder.review_changes = MagicMock()
        self.coder.record_exchange = MagicMock()
        
        self.coder.process_architect_change_proposal(exchange, is_plan_change=True)
        self.coder.execute_changes.assert_called_once()
        self.coder.review_changes.assert_not_called()  # No editor response yet
        self.coder.record_exchange.assert_called_once()

    def test_execute_changes(self):
        """Test executing changes via editor coder."""
        exchange = ArchitectExchange("Here's my proposal...")
        editor_response = "Changes implemented..."
        
        # Mock editor coder
        with patch.object(self.coder, 'create_coder') as mock_create:
            mock_editor = MagicMock()
            mock_editor.partial_response_content = editor_response
            mock_editor.total_cost = 0.001
            mock_editor.aider_commit_hashes = ["abc123"]
            mock_create.return_value = mock_editor
            
            self.coder.execute_changes(exchange, is_plan_change=False)
            
            # Verify editor was created and run
            mock_create.assert_called_once()
            mock_editor.run.assert_called_once()
            
            # Verify exchange was updated
            self.assertTrue(exchange.has_editor_response())
            self.assertEqual(exchange.messages[-1]["content"], editor_response)
            
            # Verify costs and hashes were transferred
            self.assertEqual(self.coder.total_cost, 0.001)
            self.assertEqual(self.coder.aider_commit_hashes, ["abc123"])

    def test_review_changes(self):
        """Test reviewing changes via reviewer coder."""
        exchange = ArchitectExchange("Here's my proposal...")
        exchange.append_editor_prompt(is_plan_change=False)
        exchange.append_editor_response("Changes implemented...")
        reviewer_response = "Changes look good..."
        
        # Mock reviewer coder
        with patch.object(self.coder, 'create_coder') as mock_create:
            mock_reviewer = MagicMock()
            mock_reviewer.partial_response_content = reviewer_response
            mock_reviewer.total_cost = 0.001
            mock_create.return_value = mock_reviewer
            
            self.coder.review_changes(exchange)
            
            # Verify reviewer was created and run
            mock_create.assert_called_once()
            mock_reviewer.run.assert_called_once()
            
            # Verify exchange was updated
            self.assertEqual(exchange.messages[-1]["content"], reviewer_response)
            
            # Verify costs were transferred
            self.assertEqual(self.coder.total_cost, 0.001)

    def test_record_exchange(self):
        """Test recording a completed exchange.

        Note: The architect's proposal is added to cur_messages by base_coder.py before
        reply_completed() is called. This test verifies that the exchange is properly
        recorded in done_messages after the changes are implemented and reviewed.
        """
        exchange = ArchitectExchange("Here's my proposal...")
        exchange.append_editor_prompt(is_plan_change=False)
        exchange.append_editor_response("Changes implemented...")
        exchange.append_reviewer_prompt()
        exchange.append_reviewer_response("Changes look good...")
        
        self.coder.record_exchange(exchange)
        
        # Verify messages were moved to done_messages
        # The done_messages will include:
        # - The exchange messages
        # - The commit message
        # - The "Understood" response
        self.assertEqual(len(self.coder.done_messages), len(exchange.messages) + 2)
        
        # Verify cur_messages was cleared after move_back_cur_messages
        self.assertEqual(len(self.coder.cur_messages), 0)
        self.assertEqual(self.coder.partial_response_content, "")


if __name__ == "__main__":
    unittest.main()
