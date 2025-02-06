import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import httpx
from llm_multiple_choice import ChoiceManager

from aider.exceptions import InvalidResponseError, SendCompletionError
from aider.llm import litellm
from aider.models import _ModelConfigImpl, _OpenAiReasoningConfigImpl, get_model_config
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
        self.test_model = _ModelConfigImpl("gpt-4")

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
        self.test_model = _ModelConfigImpl("gpt-4")

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
            send_completion(self.test_model, ["message"], None, False)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Bad Request", str(context.exception))

    def test_transform_messages_for_o3(self):
        """Test basic system-to-user message conversion for o3 models."""
        from aider.sendchat import transform_messages_for_o3

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
        self.test_model = _ModelConfigImpl("gpt-4")

        # Set up the mock to return invalid response
        mock_completion.return_value = invalid_response

        # Call send_completion and verify it raises InvalidResponseError
        with self.assertRaises(InvalidResponseError) as context:
            send_completion(self.test_model, ["message"], None, False)

        self.assertIn("has no choices attribute", str(context.exception))

    @patch("litellm.completion")
    @patch("builtins.print")
    def test_send_completion_empty_choices(self, mock_print, mock_completion):
        # Create a response with empty choices list
        invalid_response = MagicMock()
        invalid_response.status_code = 200
        invalid_response.choices = []
        invalid_response.text = ""
        self.test_model = _ModelConfigImpl("gpt-4")

        # Set up the mock to return invalid response
        mock_completion.return_value = invalid_response

        # Call send_completion and verify it raises InvalidResponseError
        with self.assertRaises(InvalidResponseError) as context:
            send_completion(self.test_model, ["message"], None, False)

        self.assertIn("empty choices list", str(context.exception))

    @patch("litellm.completion")
    def test_send_completion_no_temperature(self, mock_completion):
        # Create a model that doesn't support temperature
        model = get_model_config("o3-mini")
        self.assertFalse(model.use_temperature)

        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "test response"
        mock_completion.return_value = mock_response

        # Call send_completion with a temperature
        send_completion(model, ["message"], None, False, temperature=0.7)

        # Verify temperature was not passed to litellm
        mock_completion.assert_called_once()
        kwargs = mock_completion.call_args.kwargs
        self.assertNotIn("temperature", kwargs)

    @patch("litellm.completion")
    def test_send_completion_reasoning_level(self, mock_completion):
        # Create a successful mock response
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"
        success_response.status_code = 200
        mock_completion.return_value = success_response

        # Test with a reasoning model
        model_config = _OpenAiReasoningConfigImpl("o3-mini")
        self.assertTrue(model_config.is_reasoning_model)

        # Call send_completion with reasoning_level
        send_completion(model_config, ["message"], None, False, reasoning_level=1)

        # Verify reasoning_effort was passed to litellm
        mock_completion.assert_called_once()
        kwargs = mock_completion.call_args.kwargs
        self.assertEqual(kwargs.get("reasoning_effort"), "high")

        # Test with a non-reasoning model
        mock_completion.reset_mock()
        model_config = _ModelConfigImpl("gpt-4")
        self.assertFalse(model_config.is_reasoning_model)

        # Call send_completion with reasoning_level
        send_completion(model_config, ["message"], None, False, reasoning_level=1)

        # Verify no reasoning parameters were passed
        mock_completion.assert_called_once()
        kwargs = mock_completion.call_args.kwargs
        self.assertNotIn("reasoning_effort", kwargs)

    @patch("litellm.completion")
    def test_parameter_layering(self, mock_completion):
        # Create a successful mock response
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"
        success_response.status_code = 200
        mock_completion.return_value = success_response

        # Create model with various parameters
        model = _ModelConfigImpl("test-model")
        model.extra_params = {"param1": "model_extra"}
        model.provider_params = {"provider_param2": "provider_value2"}
        model.provider_headers = {"provider_header3": "provider_value3"}

        # Call with extra params that should override model params
        extra_params = {
            "param1": "extra_override",
            "param3": "extra_new"
        }

        send_completion(model, ["message"], None, False, extra_params=extra_params)

        # Verify parameter layering
        mock_completion.assert_called_once()
        kwargs = mock_completion.call_args.kwargs
        
        # Extra params should override model extra params
        self.assertEqual(kwargs.get("extra_params", {}).get("param1"), "extra_override")
        
        # Provider params should be preserved
        self.assertEqual(kwargs.get("extra_params", {}).get("param2"), "model_provider")
        
        # New extra params should be included
        self.assertEqual(kwargs.get("extra_params", {}).get("param3"), "extra_new")
        
        # Provider headers should be preserved
        self.assertEqual(kwargs.get("extra_headers"), {"header1": "model_header"})

        # Verify parameter layering
        mock_completion.assert_called_once()
        kwargs = mock_completion.call_args.kwargs
        
        # Extra params should override model extra params
        self.assertEqual(kwargs.get("param1"), "extra_override")
        
        # Provider params should be preserved
        self.assertEqual(kwargs.get("param2"), "model_provider")
        
        # New extra params should be included
        self.assertEqual(kwargs.get("param3"), "extra_new")
        
        # Provider headers should be preserved
        self.assertEqual(kwargs.get("extra_headers"), {"header1": "model_header"})

    @patch("litellm.completion") 
    def test_reasoning_parameter_precedence(self, mock_completion):
        # Create a successful mock response
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success response"
        success_response.status_code = 200
        mock_completion.return_value = success_response

        # Create reasoning model with extra params
        model = _OpenAiReasoningConfigImpl("o3-mini")
        model.extra_params = {"reasoning_effort": "low"}

        # Call with extra params that should NOT override reasoning level
        extra_params = {"reasoning_effort": "medium"}
        
        # reasoning_level should take precedence over both model.extra_params and extra_params
        send_completion(model, ["message"], None, False, 
                       extra_params=extra_params, reasoning_level=1)

        # Verify reasoning_level took precedence
        mock_completion.assert_called_once()
        kwargs = mock_completion.call_args.kwargs
        self.assertEqual(kwargs.get("extra_params", {}).get("reasoning_effort"), "high")
