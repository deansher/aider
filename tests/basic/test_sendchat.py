import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import httpx
from llm_multiple_choice import ChoiceManager

from aider.exceptions import InvalidResponseError, SendCompletionError
from aider.llm import litellm
from aider.models import Model
from aider.sendchat import (
    analyze_assistant_response,
    send_completion,
    simple_send_with_retries,
)


@dataclass
class MockModel:
    name: str
    extra_params: dict = None


class PrintCalled(Exception):
    pass


class TestSendChat(unittest.TestCase):
    def setUp(self):
        self.test_model = Model("gpt-4")

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_simple_send_with_retries_rate_limit_error(self, mock_print, mock_completion):
        # Create a successful mock response for the second attempt
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"
        success_response.status_code = 200

        # Set up the mock to raise then succeed
        mock_completion.side_effect = [
            litellm.exceptions.RateLimitError(
                "rate limit exceeded",
                response=None,
                llm_provider="llm_provider",
                model="model",
            ),
            success_response,
        ]

        # Call the simple_send_with_retries method
        result = simple_send_with_retries(self.test_model, [{"role": "user", "content": "message"}])
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
        self.test_model = Model("gpt-4")

    @patch("aider.sendchat.send_completion")
    def test_analyze_assistant_response_retry_success(self, mock_send):
        # Mock responses: first invalid, then valid
        invalid_response = MagicMock()
        invalid_response.choices = [MagicMock()]
        invalid_response.choices[0].message.content = "invalid"

        valid_response = MagicMock()
        valid_response.choices = [MagicMock()]
        valid_response.choices[0].message.content = "1"

        mock_send.side_effect = [(None, invalid_response), (None, valid_response)]

        # Create a mock model object
        model = MockModel(name="test-model")

        # Call should succeed after retry
        result = analyze_assistant_response(
            self.choice_manager,
            self.introduction,
            model,  # Pass model object instead of model name
            "test response",
        )

        # Verify the result contains the expected choice
        self.assertTrue(result.has(self.choice1))
        self.assertFalse(result.has(self.choice2))

        # Verify send_completion was called twice
        self.assertEqual(mock_send.call_count, 2)

        # Verify that the second call included the error information
        second_call_args = mock_send.call_args_list[1][1]
        messages = second_call_args["messages"]
        self.assertIn("Previous Error", messages[0]["content"])
        self.assertIn("invalid", messages[0]["content"])

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_simple_send_with_retries_connection_error(self, mock_print, mock_completion):
        # Create a successful mock response for the second attempt
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"
        success_response.status_code = 200

        # Set up the mock to raise then succeed
        mock_completion.side_effect = [
            httpx.ConnectError("Connection error"),
            success_response,
        ]

        # Call the simple_send_with_retries method
        result = simple_send_with_retries(self.test_model, [{"role": "user", "content": "message"}])
        self.assertEqual(result, "Success response")
        mock_print.assert_called_once()

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_simple_send_with_retries_invalid_response(self, mock_print, mock_completion):
        # Create a successful mock response for the second attempt
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"
        success_response.status_code = 200

        # Create an invalid response for the first attempt
        invalid_response = MagicMock()
        invalid_response.choices = []
        invalid_response.status_code = 200

        # Set up the mock to return invalid response then succeed
        mock_completion.side_effect = [
            InvalidResponseError("Invalid response"),
            success_response,
        ]

        # Call the simple_send_with_retries method
        result = simple_send_with_retries(self.test_model, ["message"])
        self.assertEqual(result, "Success response")
        mock_print.assert_called_once()

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_simple_send_with_retries_none_response(self, mock_print, mock_completion):
        # Create a successful mock response for the second attempt
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"
        success_response.status_code = 200

        # Set up the mock to return None then succeed
        mock_completion.side_effect = [
            InvalidResponseError("None response"),
            success_response,
        ]

        # Call the simple_send_with_retries method
        result = simple_send_with_retries(self.test_model, ["message"])
        self.assertEqual(result, "Success response")
        mock_print.assert_called_once()

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_send_completion_non_200_status(self, mock_print, mock_completion):
        # Create a response with non-200 status code
        error_response = MagicMock()
        error_response.status_code = 400
        error_response.text = "Bad Request"

        # Set up the mock to return error response
        mock_completion.return_value = error_response

        # Call send_completion and verify it raises SendCompletionError
        with self.assertRaises(SendCompletionError) as context:
            send_completion("model", ["message"], None, False)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Bad Request", str(context.exception))

    def test_transform_messages_for_o3(self):
        """Test basic system-to-user message conversion for o3 models."""
        from aider.sendchat import transform_messages_for_o3
        """Test basic system-to-user message conversion for o3 models."""
        # Test single system message
        messages = [{"role": "system", "content": "You are a helpful assistant"}]
        transformed = transform_messages_for_o3(messages)
        self.assertEqual(len(transformed), 1)
        self.assertEqual(transformed[0]["role"], "user")
        self.assertEqual(transformed[0]["content"], messages[0]["content"])

        # Test multiple system messages
        messages = [
            {"role": "system", "content": "System message 1"},
            {"role": "system", "content": "System message 2"},
        ]
        transformed = transform_messages_for_o3(messages)
        self.assertEqual(len(transformed), 2)
        self.assertTrue(all(msg["role"] == "user" for msg in transformed))
        self.assertEqual([msg["content"] for msg in transformed], 
                        [msg["content"] for msg in messages])

        # Test order preservation with mixed message types
        messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "system", "content": "Another system message"},
            {"role": "assistant", "content": "Assistant message"},
        ]
        transformed = transform_messages_for_o3(messages)
        self.assertEqual(len(transformed), 4)
        self.assertEqual(transformed[0]["role"], "user")  # was system
        self.assertEqual(transformed[1]["role"], "user")  # was user
        self.assertEqual(transformed[2]["role"], "user")  # was system
        self.assertEqual(transformed[3]["role"], "assistant")  # unchanged
        self.assertEqual([msg["content"] for msg in transformed],
                        [msg["content"] for msg in messages])

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_send_completion_missing_choices(self, mock_print, mock_completion):
        # Create a response missing choices attribute
        invalid_response = MagicMock()
        invalid_response.status_code = 200
        # Remove choices attribute
        del invalid_response.choices
        self.test_model = Model("gpt-4")

        # Set up the mock to return invalid response
        mock_completion.return_value = invalid_response

        # Call send_completion and verify it raises InvalidResponseError
        with self.assertRaises(InvalidResponseError) as context:
            send_completion("model", ["message"], None, False)

        self.assertIn("has no choices attribute", str(context.exception))

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_send_completion_empty_choices(self, mock_print, mock_completion):
        # Create a response with empty choices list
        invalid_response = MagicMock()
        invalid_response.status_code = 200
        invalid_response.choices = []
        invalid_response.text = ""
        self.test_model = Model("gpt-4")

        # Set up the mock to return invalid response
        mock_completion.return_value = invalid_response

        # Call send_completion and verify it raises InvalidResponseError
        with self.assertRaises(InvalidResponseError) as context:
            send_completion("model", ["message"], None, False)

        self.assertIn("empty choices list", str(context.exception))
