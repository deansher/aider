import unittest
from unittest.mock import MagicMock, patch

from aider.coders.architect_coder import ArchitectCoder, ArchitectExchange, ArchitectPhase
from aider.coders.architect_prompts import ArchitectPrompts
from aider.io import InputOutput
from aider.models import Model


class TestArchitectExchange(unittest.TestCase):
    """Test the ArchitectExchange class that manages architect-editor-reviewer exchanges."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.model = Model("gpt-3.5-turbo")
        self.architect_prompts = ArchitectPrompts(
            main_model=self.model,
            editor_model=self.model.editor_model,
        )
        self.architect_response = "Here's my proposal for changes..."
        self.exchange = ArchitectExchange(self.architect_prompts, self.architect_response)

    def test_init(self):
        """Test initialization with architect response."""
        self.assertEqual(len(self.exchange.messages), 1)
        self.assertEqual(self.exchange.messages[0]["role"], "assistant")
        self.assertEqual(self.exchange.messages[0]["content"], self.architect_response)
        self.assertEqual(self.exchange.architect_prompts, self.architect_prompts)

    def test_append_editor_prompt(self):
        """Test appending editor prompts for both plan and non-plan changes."""
        # Mock the prompt methods
        plan_prompt = "Execute plan changes..."
        non_plan_prompt = "Execute non-plan changes..."
        self.architect_prompts.get_approved_plan_changes_prompt = MagicMock(
            return_value=plan_prompt
        )
        self.architect_prompts.get_approved_non_plan_changes_prompt = MagicMock(
            return_value=non_plan_prompt
        )

        # Test plan changes prompt
        prompt = self.exchange.append_editor_prompt(is_plan_change=True)
        self.assertEqual(prompt, plan_prompt)
        self.assertEqual(self.exchange.messages[-1]["role"], "user")
        self.assertEqual(self.exchange.messages[-1]["content"], prompt)
        self.architect_prompts.get_approved_plan_changes_prompt.assert_called_once()

        # Test non-plan changes prompt
        prompt = self.exchange.append_editor_prompt(is_plan_change=False)
        self.assertEqual(prompt, non_plan_prompt)
        self.assertEqual(self.exchange.messages[-1]["role"], "user")
        self.assertEqual(self.exchange.messages[-1]["content"], prompt)
        self.architect_prompts.get_approved_non_plan_changes_prompt.assert_called_once()

    def test_append_editor_response(self):
        """Test appending editor response."""
        response = "I've implemented the changes..."
        self.exchange.append_editor_response(response)
        self.assertEqual(self.exchange.messages[-1]["role"], "assistant")
        self.assertEqual(self.exchange.messages[-1]["content"], response)

    def test_append_reviewer_prompt(self):
        """Test appending reviewer prompt."""
        review_prompt = "Please review changes..."
        self.architect_prompts.get_review_changes_prompt = MagicMock(return_value=review_prompt)

        prompt = self.exchange.append_reviewer_prompt()
        self.assertEqual(prompt, review_prompt)
        self.assertEqual(self.exchange.messages[-1]["role"], "user")
        self.assertEqual(self.exchange.messages[-1]["content"], prompt)
        self.architect_prompts.get_review_changes_prompt.assert_called_once()

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

    def test_get_messages_by_phase(self):
        """Test filtering messages by phase."""
        # Initial state has just the architect proposal
        step1_msgs = self.exchange.get_messages_by_phase(ArchitectPhase.STEP1_PROPOSE)
        self.assertEqual(len(step1_msgs), 1)
        self.assertEqual(step1_msgs[0]["content"], self.architect_response)

        # Add implementation phase messages
        self.exchange.append_editor_prompt(is_plan_change=False)
        self.exchange.append_editor_response("Changes made")
        step2_msgs = self.exchange.get_messages_by_phase(ArchitectPhase.STEP2_IMPLEMENT)
        self.assertEqual(len(step2_msgs), 2)
        self.assertEqual(step2_msgs[1]["content"], "Changes made")

        # Add review phase messages
        self.exchange.append_reviewer_prompt()
        self.exchange.append_reviewer_response("Review complete")
        step3_msgs = self.exchange.get_messages_by_phase(ArchitectPhase.STEP3_REVIEW)
        self.assertEqual(len(step3_msgs), 2)
        self.assertEqual(step3_msgs[1]["content"], "Review complete")

    def test_phase_transitions(self):
        """Test that messages are tagged with correct phases through a complete exchange."""
        # Start with proposal phase
        self.assertEqual(len(self.exchange.get_messages_by_phase(ArchitectPhase.STEP1_PROPOSE)), 1)
        self.assertEqual(len(self.exchange.get_messages_by_phase(ArchitectPhase.STEP2_IMPLEMENT)), 0)
        self.assertEqual(len(self.exchange.get_messages_by_phase(ArchitectPhase.STEP3_REVIEW)), 0)

        # Transition to implementation phase
        self.exchange.append_editor_prompt(is_plan_change=False)
        self.exchange.append_editor_response("Changes made")
        self.assertEqual(len(self.exchange.get_messages_by_phase(ArchitectPhase.STEP1_PROPOSE)), 1)
        self.assertEqual(len(self.exchange.get_messages_by_phase(ArchitectPhase.STEP2_IMPLEMENT)), 2)
        self.assertEqual(len(self.exchange.get_messages_by_phase(ArchitectPhase.STEP3_REVIEW)), 0)

        # Transition to review phase
        self.exchange.append_reviewer_prompt()
        self.exchange.append_reviewer_response("Review complete")
        self.assertEqual(len(self.exchange.get_messages_by_phase(ArchitectPhase.STEP1_PROPOSE)), 1)
        self.assertEqual(len(self.exchange.get_messages_by_phase(ArchitectPhase.STEP2_IMPLEMENT)), 2)
        self.assertEqual(len(self.exchange.get_messages_by_phase(ArchitectPhase.STEP3_REVIEW)), 2)

    def test_empty_exchange(self):
        """Test behavior with minimal messages in the exchange."""
        # Create exchange with just the initial proposal
        minimal_exchange = ArchitectExchange(self.architect_prompts, "Minimal proposal")
        
        # Verify phase counts
        self.assertEqual(len(minimal_exchange.get_messages_by_phase(ArchitectPhase.STEP1_PROPOSE)), 1)
        self.assertEqual(len(minimal_exchange.get_messages_by_phase(ArchitectPhase.STEP2_IMPLEMENT)), 0)
        self.assertEqual(len(minimal_exchange.get_messages_by_phase(ArchitectPhase.STEP3_REVIEW)), 0)

        # Verify message content
        self.assertEqual(minimal_exchange.get_messages()[0]["content"], "Minimal proposal")


class TestArchitectCoder(unittest.TestCase):
    """Test the ArchitectCoder class that coordinates architecture decisions."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.model = Model("gpt-3.5-turbo")
        self.io = InputOutput()
        self.coder = ArchitectCoder.create(self.model, "architect", io=self.io)

    def test_init(self):
        """Test initialization of ArchitectCoder."""
        self.assertIsInstance(self.coder.architect_prompts, ArchitectPrompts)
        self.assertEqual(self.coder.gpt_prompts, self.coder.architect_prompts)

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
        exchange = ArchitectExchange(self.coder.architect_prompts, "Here's my proposal...")

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
        exchange = ArchitectExchange(self.coder.architect_prompts, "Here's my proposal...")
        editor_response = "Changes implemented..."

        # Mock editor coder
        with patch.object(self.coder, "create_coder") as mock_create:
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
        exchange = ArchitectExchange(self.coder.architect_prompts, "Here's my proposal...")
        exchange.append_editor_prompt(is_plan_change=False)
        exchange.append_editor_response("Changes implemented...")
        reviewer_response = "Changes look good..."

        # Mock reviewer coder
        with patch.object(self.coder, "create_coder") as mock_create:
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
        
        This test verifies that:
        1. Only Step 1 (proposal) and Step 3 (review) messages are retained
        2. Step 2 (implementation) messages are properly excluded
        3. Transition messages are inserted to explain the flow
        4. Implementation details don't leak into future exchanges
        """
        # Create an exchange with all three steps
        exchange = ArchitectExchange(self.coder.architect_prompts, "Here's my proposal...")
        exchange.append_editor_prompt(is_plan_change=False)
        exchange.append_editor_response("Changes implemented...")
        exchange.append_reviewer_prompt()
        exchange.append_reviewer_response("Changes look good...")

        # Record the exchange
        self.coder.record_exchange(exchange)

        # Get the recorded messages
        recorded_messages = self.coder.done_messages

        # Verify Step 1 messages were retained
        step1_messages = exchange.get_messages_by_phase(ArchitectPhase.STEP1_PROPOSE)
        for msg in step1_messages:
            self.assertIn(msg, recorded_messages)

        # Verify Step 2 messages were excluded
        step2_messages = exchange.get_messages_by_phase(ArchitectPhase.STEP2_IMPLEMENT)
        for msg in step2_messages:
            self.assertNotIn(msg, recorded_messages)

        # Verify Step 3 messages were retained
        step3_messages = exchange.get_messages_by_phase(ArchitectPhase.STEP3_REVIEW)
        for msg in step3_messages:
            self.assertIn(msg, recorded_messages)

        # Verify transition messages were inserted
        transition_messages = [
            {"role": "user", "content": self.coder.architect_prompts.IMPLEMENTATION_COMPLETE},
            {"role": "assistant", "content": self.coder.architect_prompts.REVIEW_BEGINS},
        ]
        for msg in transition_messages:
            self.assertIn(msg, recorded_messages)

        # Verify commit message was added
        self.assertIn(
            {"role": "user", "content": self.coder.architect_prompts.changes_committed_message},
            recorded_messages
        )

        # Verify cur_messages was cleared after move_back_cur_messages
        self.assertEqual(len(self.coder.cur_messages), 0)
        self.assertEqual(self.coder.partial_response_content, "")


if __name__ == "__main__":
    unittest.main()
