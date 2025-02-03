import unittest
from unittest.mock import ANY, MagicMock, patch

from aider.models import Model, get_model_info, sanity_check_model, sanity_check_models


class TestModels(unittest.TestCase):
    def test_get_model_info_nonexistent(self):
        info = get_model_info("non-existent-model")
        self.assertEqual(info, {})

    def test_max_context_tokens(self):
        model = Model("gpt-3.5-turbo")
        self.assertEqual(model.info["max_input_tokens"], 16385)

        model = Model("gpt-3.5-turbo-16k")
        self.assertEqual(model.info["max_input_tokens"], 16385)

        model = Model("gpt-3.5-turbo-1106")
        self.assertEqual(model.info["max_input_tokens"], 16385)

        model = Model("gpt-4")
        self.assertEqual(model.info["max_input_tokens"], 8 * 1024)

        model = Model("gpt-4-32k")
        self.assertEqual(model.info["max_input_tokens"], 32 * 1024)

        model = Model("gpt-4-0613")
        self.assertEqual(model.info["max_input_tokens"], 8 * 1024)

        # o3-mini and o1 share the same 200k token context window
        model = Model("o3-mini")
        self.assertEqual(model.info["max_input_tokens"], 200000)

        # Test o3-mini model settings
        model = Model("o3-mini")
        self.assertTrue(model.is_reasoning_model)
        self.assertEqual(model.edit_format, "whole")
        self.assertEqual(model.weak_model_name, "gpt-4o")
        self.assertEqual(model.editor_model_name, "o3-mini")
        self.assertEqual(model.editor_edit_format, "editor-diff")

    @patch("os.environ")
    def test_sanity_check_model_all_set(self, mock_environ):
        mock_environ.get.return_value = "dummy_value"
        mock_io = MagicMock()
        model = MagicMock()
        model.name = "test-model"
        model.missing_keys = ["API_KEY1", "API_KEY2"]
        model.keys_in_environment = True
        model.info = {"some": "info"}

        sanity_check_model(mock_io, model)

        mock_io.tool_output.assert_called()
        calls = mock_io.tool_output.call_args_list
        self.assertIn("- API_KEY1: Set", str(calls))
        self.assertIn("- API_KEY2: Set", str(calls))

    @patch("os.environ")
    def test_sanity_check_model_not_set(self, mock_environ):
        mock_environ.get.return_value = ""
        mock_io = MagicMock()
        model = MagicMock()
        model.name = "test-model"
        model.missing_keys = ["API_KEY1", "API_KEY2"]
        model.keys_in_environment = True
        model.info = {"some": "info"}

        sanity_check_model(mock_io, model)

        mock_io.tool_output.assert_called()
        calls = mock_io.tool_output.call_args_list
        self.assertIn("- API_KEY1: Not set", str(calls))
        self.assertIn("- API_KEY2: Not set", str(calls))

    def test_sanity_check_models_bogus_editor(self):
        mock_io = MagicMock()
        main_model = Model("gpt-4")
        main_model.editor_model = Model("bogus-model")

        result = sanity_check_models(mock_io, main_model)

        self.assertTrue(
            result
        )  # Should return True because there's a problem with the editor model
        mock_io.tool_warning.assert_called_with(ANY)  # Ensure a warning was issued
        self.assertGreaterEqual(mock_io.tool_warning.call_count, 1)  # Expect at least one warning
        warning_messages = [call.args[0] for call in mock_io.tool_warning.call_args_list]
        self.assertTrue(
            any("bogus-model" in msg for msg in warning_messages)
        )  # Check that one of the warnings mentions the bogus model

        # Test o3-mini with bogus editor
        main_model = Model("o3-mini")
        main_model.editor_model = Model("bogus-model")

        result = sanity_check_models(mock_io, main_model)

        self.assertTrue(result)  # Should return True because there's a problem with the editor model
        warning_messages = [call.args[0] for call in mock_io.tool_warning.call_args_list]
        self.assertTrue(
            any("bogus-model" in msg for msg in warning_messages)
        )  # Check that one of the warnings mentions the bogus model


if __name__ == "__main__":
    unittest.main()
