import unittest
from unittest.mock import MagicMock, patch

import httpx
from llm_multiple_choice import ChoiceManager, InvalidChoicesResponseError

from aider.llm import litellm
from aider.sendchat import analyze_chat_situation, simple_send_with_retries


class PrintCalled(Exception):
    pass


class TestSendChat(unittest.TestCase):
    @patch("litellm.completion")
    @patch("builtins.print")
    def test_simple_send_with_retries_rate_limit_error(self, mock_print, mock_completion):
        mock = MagicMock()
        mock.status_code = 500

        # Create a successful mock response for the second attempt
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"

        # Set up the mock to raise then succeed
        mock_completion.side_effect = [
            litellm.exceptions.RateLimitError(
                "rate limit exceeded",
                response=mock,
                llm_provider="llm_provider",
                model="model",
            ),
            success_response,
        ]

        # Call the simple_send_with_retries method
        result = simple_send_with_retries("model", ["message"])
        self.assertEqual(result, "Success response")
        mock_print.assert_called_once()


class TestAnalyzeChatSituation(unittest.TestCase):
    def setUp(self):
        self.choice_manager = ChoiceManager()
        section = self.choice_manager.add_section("Test section")
        self.choice1 = section.add_choice("First choice")
        self.choice2 = section.add_choice("Second choice")

        self.messages = [{"role": "user", "content": "test message"}]
        self.model_name = "test-model"
        self.introduction = "Test introduction"

    @patch("aider.sendchat.send_completion")
    def test_analyze_chat_situation_success(self, mock_send):
        # Mock a valid response from the LLM
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "1"
        mock_send.return_value = (None, mock_response)

        # Call analyze_chat_situation and verify the result
        result = analyze_chat_situation(
            self.choice_manager,
            self.introduction,
            self.model_name,
            self.messages,
        )
        self.assertTrue(result.has(self.choice1))
        self.assertFalse(result.has(self.choice2))

    @patch("aider.sendchat.send_completion")
    def test_analyze_chat_situation_invalid_response(self, mock_send):
        # Mock an invalid response from the LLM
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "invalid"
        mock_send.return_value = (None, mock_response)

        # Verify that invalid response raises appropriate error
        with self.assertRaises(InvalidChoicesResponseError):
            analyze_chat_situation(
                self.choice_manager,
                self.introduction,
                self.model_name,
                self.messages,
            )

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_simple_send_with_retries_connection_error(self, mock_print, mock_completion):
        # Create a successful mock response for the second attempt
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"

        # Set up the mock to raise then succeed
        mock_completion.side_effect = [
            httpx.ConnectError("Connection error"),
            success_response,
        ]

        # Call the simple_send_with_retries method
        result = simple_send_with_retries("model", ["message"])
        self.assertEqual(result, "Success response")
        mock_print.assert_called_once()

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_simple_send_with_retries_invalid_response(self, mock_print, mock_completion):
        # Create a successful mock response for the second attempt
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"

        # Create an invalid response for the first attempt
        invalid_response = MagicMock()
        invalid_response.choices = []

        # Set up the mock to return invalid response then succeed
        mock_completion.side_effect = [invalid_response, success_response]

        # Call the simple_send_with_retries method
        result = simple_send_with_retries("model", ["message"])
        self.assertEqual(result, "Success response")
        mock_print.assert_called_once()
