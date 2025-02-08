# flake8: noqa: E501

import tempfile
import unittest
from pathlib import Path

from aider.coders import Coder
from aider.coders import editblock_coder as eb
from aider.io import InputOutput
from aider.models import _ModelConfigImpl


class TestUtils(unittest.TestCase):
    """Test suite for editblock_coder.py focusing on key behaviors.
    
    Our testing strategy focuses on three essential aspects:
    
    1. Success Cases:
       - Verify that exact matches work correctly
       - Confirm only first occurrence is replaced
       - Test with representative real-world content
    
    2. Failure Cases:
       - Verify that similarity below 0.95 triggers failure
       - Test with realistic transcription errors
       - Confirm even minor differences fail
    
    3. Parsing Tests:
       - Verify filename extraction and validation
       - Test edit block parsing and validation
       - Confirm proper handling of edge cases
    
    Design Decision:
    We intentionally use raw diff-match-patch with a strict 0.95 similarity threshold.
    Any case that produces similarity below 0.95 (even when differences are just
    whitespace) raises a ValueError. This enforces our requirement that the LLM must
    be highly accurate in its transcription of existing code.
    """
    
    def setUp(self):
        self.GPT35 = _ModelConfigImpl("gpt-3.5-turbo")

    def test_strip_filename(self):
        # Test basic cases
        self.assertEqual(eb.strip_filename("file.py"), "file.py")
        self.assertEqual(eb.strip_filename(" file.py "), "file.py")

        # Test individual removals
        self.assertEqual(eb.strip_filename("#file.py"), "file.py")
        self.assertEqual(eb.strip_filename("file.py:"), "file.py")
        self.assertEqual(eb.strip_filename("`file.py`"), "file.py")

        # Test combinations
        self.assertEqual(eb.strip_filename("#file.py:"), "file.py")
        self.assertEqual(eb.strip_filename("# `file.py`"), "file.py")
        self.assertEqual(eb.strip_filename("# `file.py:"), "`file.py")

        # Test empty results
        self.assertEqual(eb.strip_filename(""), "")
        self.assertEqual(eb.strip_filename("  "), "")

    def test_find_filename(self):
        # Test with valid_fnames provided
        valid_fnames = ["file1.py", "dir/file2.py", "path/to/file3.py"]

        # Test exact matches
        self.assertEqual(eb.find_filename("file1.py", valid_fnames), "file1.py")
        self.assertEqual(eb.find_filename("dir/file2.py", valid_fnames), "dir/file2.py")

        # Test basename matches
        self.assertEqual(eb.find_filename("file2.py", valid_fnames), "dir/file2.py")
        self.assertEqual(eb.find_filename("file3.py", valid_fnames), "path/to/file3.py")

        # Test with strippable characters
        self.assertEqual(eb.find_filename("#file1.py:", valid_fnames), "file1.py")
        self.assertEqual(eb.find_filename("`dir/file2.py`", valid_fnames), "dir/file2.py")

        # Test no matches
        self.assertIsNone(eb.find_filename("nonexistent.py", valid_fnames))
        self.assertIsNone(eb.find_filename("", valid_fnames))

        # Test without valid_fnames
        self.assertEqual(eb.find_filename("newfile.py", None), "newfile.py")
        self.assertEqual(eb.find_filename("path/to/newfile.py", None), "path/to/newfile.py")
        self.assertIsNone(eb.find_filename("invalid", None))  # No extension

    def test_strip_quoted_wrapping(self):
        input_text = (
            "filename.ext\n```\nWe just want this content\nNot the filename and triple quotes\n```"
        )
        expected_output = "We just want this content\nNot the filename and triple quotes\n"
        result = eb.strip_quoted_wrapping(input_text, "filename.ext")
        self.assertEqual(result, expected_output)

    def test_strip_quoted_wrapping_no_filename(self):
        input_text = "```\nWe just want this content\nNot the triple quotes\n```"
        expected_output = "We just want this content\nNot the triple quotes\n"
        result = eb.strip_quoted_wrapping(input_text)
        self.assertEqual(result, expected_output)

    def test_strip_quoted_wrapping_no_wrapping(self):
        input_text = "We just want this content\nNot the triple quotes\n"
        expected_output = "We just want this content\nNot the triple quotes\n"
        result = eb.strip_quoted_wrapping(input_text)
        self.assertEqual(result, expected_output)

    def test_find_original_update_blocks_basic(self):
        edit = (
            "\nHere's the change:\n\n"
            "foo.txt\n"
            "```text\n"
            "<<<<<<< SEARCH\n"
            "def calculate_total(numbers):\n"
            "    total = 0\n"
            "    for num in numbers:\n"
            "        total += num\n"
            "    return total\n"
            "=======\n"
            "def calculate_total(numbers):\n"
            "    return sum(numbers)\n"
            ">>>>>>> REPLACE\n"
            "```\n\n"
            "Hope you like it!\n"
        )
        edits = list(eb.find_original_update_blocks(edit))
        self.assertEqual(edits, [("foo.txt", 
            "def calculate_total(numbers):\n"
            "    total = 0\n"
            "    for num in numbers:\n"
            "        total += num\n"
            "    return total\n",
            "def calculate_total(numbers):\n"
            "    return sum(numbers)\n")])

    def test_find_original_update_blocks_shell_commands(self):
        edit = (
            "\nHere's what to do:\n\n"
            "```bash\n"
            'echo "Hello"\n'
            "mv old.txt new.txt\n"
            "```\n\n"
            "And then this change:\n\n"
            "foo.txt\n"
            "```text\n"
            "<<<<<<< SEARCH\n"
            "Two\n"
            "=======\n"
            "Tooooo\n"
            ">>>>>>> REPLACE\n"
            "```\n"
        )
        edits = list(eb.find_original_update_blocks(edit))
        self.assertEqual(len(edits), 2)
        self.assertEqual(edits[0], (None, 'echo "Hello"\nmv old.txt new.txt\n'))
        self.assertEqual(edits[1], ("foo.txt", "Two\n", "Tooooo\n"))

    def test_find_original_update_blocks_new_file(self):
        edit = (
            '\nCreate a new file:\n\n'
            'path/to/new_module.py\n'
            '```text\n'
            '<<<<<<< SEARCH\n'
            '=======\n'
            'def main():\n'
            '    """Print a friendly greeting."""\n'
            '    print("Welcome to the application!")\n'
            '    return 0\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
            '>>>>>>> REPLACE\n'
            '```\n'
        )
        edits = list(eb.find_original_update_blocks(edit))
        self.assertEqual(edits, [("path/to/new_module.py", "", (
            'def main():\n'
            '    """Print a friendly greeting."""\n'
            '    print("Welcome to the application!")\n'
            '    return 0\n\n'
            'if __name__ == "__main__":\n'
            '    main()\n'
        ))])

    def test_find_original_update_blocks_validation(self):
        # Test missing filename
        edit = (
            "```text\n"
            "<<<<<<< SEARCH\n"
            "Two\n"
            "=======\n"
            "Tooooo\n"
            ">>>>>>> REPLACE\n"
            "```"
        )
        with self.assertRaises(ValueError) as cm:
            list(eb.find_original_update_blocks(edit))
        self.assertIn("filename", str(cm.exception))

        # Test unclosed block
        edit = (
            "foo.txt\n"
            "```text\n"
            "<<<<<<< SEARCH\n"
            "Two\n"
            "=======\n"
            "Tooooo\n"
        )
        with self.assertRaises(ValueError) as cm:
            list(eb.find_original_update_blocks(edit))
        self.assertIn("Expected `>>>>>>> REPLACE` or `=======`", str(cm.exception))

        # Test missing fence
        edit = (
            "foo.txt\n"
            "<<<<<<< SEARCH\n"
            "Two\n"
            "=======\n"
            "Tooooo\n"
            ">>>>>>> REPLACE\n"
        )
        with self.assertRaises(ValueError) as cm:
            list(eb.find_original_update_blocks(edit))
        self.assertIn("must begin with a filename and a fence", str(cm.exception))

    def test_find_original_update_blocks_no_final_newline(self):
        edit = (
            "\n"
            "aider/coder.py\n"
            "```python\n"
            "<<<<<<< SEARCH\n"
            "            self.console.print(\"[red]^C again to quit\")\n"
            "=======\n"
            "            self.io.tool_error(\"^C again to quit\")\n"
            ">>>>>>> REPLACE\n"
            "```\n\n"
            "aider/coder.py\n"
            "```python\n"
            "<<<<<<< SEARCH\n"
            "            self.io.tool_error(\"Malformed ORIGINAL/UPDATE blocks, retrying...\")\n"
            "            self.io.tool_error(err)\n"
            "=======\n"
            "            self.io.tool_error(\"Malformed ORIGINAL/UPDATE blocks, retrying...\")\n"
            "            self.io.tool_error(str(err))\n"
            ">>>>>>> REPLACE\n\n"
            "aider/coder.py\n"
            "```python\n"
            "<<<<<<< SEARCH\n"
            "            self.console.print(\"[red]Unable to get commit message from gpt-3.5-turbo. Use /commit to try again.\\n\")\n"
            "=======\n"
            "            self.io.tool_error(\"Unable to get commit message from gpt-3.5-turbo. Use /commit to try again.\")\n"
            ">>>>>>> REPLACE\n"
            "```\n\n"
            "aider/coder.py\n"
            "```python\n"
            "<<<<<<< SEARCH\n"
            "            self.console.print(\"[red]Skipped commit.\")\n"
            "=======\n"
            "            self.io.tool_error(\"Skipped commit.\")\n"
            ">>>>>>> REPLACE\n"
            "```"
        )

        # Should not raise a ValueError
        list(eb.find_original_update_blocks(edit))

    def test_incomplete_edit_block_missing_filename(self):
        edit = (
            "\nNo problem! Here are the changes to patch `subprocess.check_output` "
            "instead of `subprocess.run` in both tests:\n\n"
            "tests/test_repomap.py\n"
            "```python\n"
            "<<<<<<< SEARCH\n"
            "    def test_check_for_ctags_failure(self):\n"
            '        with patch("subprocess.run") as mock_run:\n'
            '            mock_run.side_effect = Exception("ctags not found")\n'
            "=======\n"
            "    def test_check_for_ctags_failure(self):\n"
            '        with patch("subprocess.check_output") as mock_check_output:\n'
            '            mock_check_output.side_effect = Exception("ctags not found")\n'
            ">>>>>>> REPLACE\n"
            "```\n\n"
            "tests/test_repomap.py\n"
            "```python\n"
            "<<<<<<< SEARCH\n"
            "    def test_check_for_ctags_success(self):\n"
            '        with patch("subprocess.run") as mock_run:\n'
            '            mock_run.return_value = CompletedProcess(args=["ctags", "--version"], returncode=0, stdout=\'\'\'{' + "\n"
            '  "_type": "tag",\n'
            '  "name": "status",\n'
            '  "path": "aider/main.py",\n'
            '  "pattern": "/^    status = main()$/",\n'
            '  "kind": "variable"\n'
            '}\'\'\')\n'
            "=======\n"
            "    def test_check_for_ctags_success(self):\n"
            '        with patch("subprocess.check_output") as mock_check_output:\n'
            '            mock_check_output.return_value = \'\'\'{' + "\n"
            '  "_type": "tag",\n'
            '  "name": "status",\n'
            '  "path": "aider/main.py",\n'
            '  "pattern": "/^    status = main()$/",\n'
            '  "kind": "variable"\n'
            '}\'\'\'\n'
            ">>>>>>> REPLACE\n"
            "```\n\n"
            "These changes replace the `subprocess.run` patches with `subprocess.check_output` "
            "patches in both `test_check_for_ctags_failure` and `test_check_for_ctags_success` tests.\n"
        )

    def test_exact_match_replaces_first_occurrence_only(self):
        """Verify exact match replacement behavior.
        
        This test is our primary success case, validating two key requirements:
        1. An exact match is correctly identified and replaced
        2. Only the first occurrence is modified
        
        The test uses realistic Python code with type hints and docstrings to
        represent typical content that the LLM would process.
        """
        whole = (
            "def validate_user(user_id: str) -> bool:\n"
            "    return check_permissions(user_id)\n\n"
            "def process_data(data: dict) -> None:\n"
            "    pass\n\n"
            "def validate_user(user_id: str) -> bool:\n"
            "    return True  # Duplicate for testing\n"
        )
        part = "def validate_user(user_id: str) -> bool:\n    return check_permissions(user_id)\n"
        replace = "def validate_user(user_id: str) -> bool:\n    return is_authorized(user_id)\n"
        
        result = eb.replace_most_similar_chunk(whole, part, replace)
        
        # Verify first occurrence was replaced
        self.assertIn("return is_authorized(user_id)", result)
        # Verify second occurrence was not changed
        self.assertIn("return True  # Duplicate for testing", result)
        
    def test_full_edit(self):
        # Create a few temporary files
        _, file1 = tempfile.mkstemp()

        with open(file1, "w", encoding="utf-8") as f:
            f.write(
                "one\n"
                "two\n"
                "three\n"
            )

        files = [file1]

        # Initialize the Coder object with the mocked IO and mocked repo
        coder = Coder.create(self.GPT35, "diff", io=InputOutput(), fnames=files)

        def mock_send(*args, **kwargs):
            coder.partial_response_content = (
                "\nDo this:\n\n"
                f"{Path(file1).name}\n"
                "```text\n"
                "<<<<<<< SEARCH\n"
                "two\n"
                "=======\n"
                "new\n"
                ">>>>>>> REPLACE\n"
                "```\n"
            )
            coder.partial_response_function_call = dict()
            return []

        coder.send = mock_send

        # Call the run method with a message
        coder.run(with_message="hi")

        content = Path(file1).read_text(encoding="utf-8")
        self.assertEqual(
            content,
            "one\n"
            "new\n"
            "three\n"
        )

    def test_full_edit_dry_run(self):
        # Create a few temporary files
        _, file1 = tempfile.mkstemp()

        orig_content = (
            "one\n"
            "two\n"
            "three\n"
        )

        with open(file1, "w", encoding="utf-8") as f:
            f.write(orig_content)

        files = [file1]

        # Initialize the Coder object with the mocked IO and mocked repo
        coder = Coder.create(
            self.GPT35,
            "diff",
            io=InputOutput(dry_run=True),
            fnames=files,
            dry_run=True,
        )

        def mock_send(*args, **kwargs):
            coder.partial_response_content = (
                "\nDo this:\n\n"
                f"{Path(file1).name}\n"
                "<<<<<<< SEARCH\n"
                "two\n"
                "=======\n" 
                "new\n"
                ">>>>>>> REPLACE\n\n"
            )
            coder.partial_response_function_call = dict()
            return []

        coder.send = mock_send

        # Call the run method with a message
        coder.run(with_message="hi")

        content = Path(file1).read_text(encoding="utf-8")
        self.assertEqual(content, orig_content)

    def test_find_original_update_blocks_multiple_same_file(self):
        edit = (
            "\nHere's the change:\n\n"
            "foo.txt\n"
            "```text\n"
            "<<<<<<< SEARCH\n"
            "one\n"
            "=======\n"
            "two\n"
            ">>>>>>> REPLACE\n\n"
            "...\n\n"
            "foo.txt\n"
            "```text\n"
            "<<<<<<< SEARCH\n"
            "three\n"
            "=======\n"
            "four\n"
            ">>>>>>> REPLACE\n"
            "```\n\n"
            "Hope you like it!\n"
        )

    def test_new_file_created_in_same_folder(self):
        edit = (
            "\n"
            "Here's the change:\n\n"
            "path/to/a/file2.txt\n"
            "```python\n"
            "<<<<<<< SEARCH\n"
            "=======\n"
            "three\n"
            ">>>>>>> REPLACE\n"
            "```\n\n"
            "another change\n\n"
            "path/to/a/file1.txt\n"
            "```python\n"
            "<<<<<<< SEARCH\n"
            "one\n"
            "=======\n"
            "two\n"
            ">>>>>>> REPLACE\n"
            "```\n\n"
            "Hope you like it!\n"
        )

        edits = list(eb.find_original_update_blocks(edit, valid_fnames=["path/to/a/file1.txt"]))
        self.assertEqual(
            edits,
            [
                ("path/to/a/file2.txt", "", "three\n"),
                ("path/to/a/file1.txt", "one\n", "two\n"),
            ],
        )

    def test_diff_match_patch_minor_inaccuracy(self):
        """Test that even minor differences trigger a failure when accuracy is below 95%.
        
        This test verifies that our strict matching requirement is enforced:
        1. We use a search block with a missing comma and a misspelling
        2. Since this produces accuracy below 95%, it should raise a ValueError
        3. This enforces our design decision that even minor transcription errors should fail
        """
        # Target content in file
        whole = "def process_data(data, options):\n    return data.process(options)\n"
        # Search block with missing comma and misspelling
        part = "def process_data(data options):\n    return data.procced(options)\n"
        # Replacement content (not used since match should fail)
        replace = "def process_data(data, options):\n    return data.transform(options)\n"
        
        with self.assertRaises(ValueError) as cm:
            eb.replace_most_similar_chunk(whole, part, replace)
        self.assertIn("SEARCH/REPLACE block failed", str(cm.exception))
        self.assertIn("transcription errors", str(cm.exception))

    def test_build_failed_edit_error_message_candidate_found(self):
        original = "def foo():\n    return 42\n"
        updated = "def foo():\n    return 43\n"
        # File content is almost the same as the original (extra space before 42) to trigger a candidate match.
        file_content = "def foo():\n    return  42\n"
        class FakeIO:
            def read_text(self, fname):
                return file_content
        from aider.coders import editblock_coder as eb
        dummy = eb.EditBlockCoder.__new__(eb.EditBlockCoder)
        dummy.io = FakeIO()
        dummy.fence = ("```", "```")
        dummy.abs_root_path = lambda path: path
        failed = [("dummy.py", original, updated)]
        passed = []
        message = dummy._build_failed_edit_error_message(failed, passed)
        self.assertIn(
            "## SearchReplaceNoExactMatch: The SEARCH block in dummy.py did not exactly match any content.",
            message
        )
        self.assertIn("Detected similarity:", message)
        self.assertIn("Unified diff between expected and candidate snippet:", message)
        self.assertNotIn("Warning:", message)

    def test_build_failed_edit_error_message_no_candidate(self):
        original = "def foo():\n    return 42\n"
        updated = "def foo():\n    return 43\n"
        file_content = "completely different content with no similar candidate\n"
        class FakeIO:
            def read_text(self, fname):
                return file_content
        from aider.coders import editblock_coder as eb
        dummy = eb.EditBlockCoder.__new__(eb.EditBlockCoder)
        dummy.io = FakeIO()
        dummy.fence = ("```", "```")
        dummy.abs_root_path = lambda path: path
        failed = [("dummy.py", original, updated)]
        passed = [("dummy.py", original, updated)]
        message = dummy._build_failed_edit_error_message(failed, passed)
        self.assertIn(
            "## SearchReplaceNoExactMatch: The SEARCH block in dummy.py did not exactly match any content.",
            message
        )
        self.assertIn("No similar candidate snippet found.", message)
        self.assertIn("Only resend fixed versions of the", message)

    def test_build_failed_edit_error_message_with_replace_exists_warning(self):
        original = "def foo():\n    return 42\n"
        updated = "def foo():\n    return 43\n"
        # File content includes the updated block content to trigger the warning.
        file_content = "def foo():\n    return 42\nadditional content\n" + updated + "\nmore content\n"
        class FakeIO:
            def read_text(self, fname):
                return file_content
        from aider.coders import editblock_coder as eb
        dummy = eb.EditBlockCoder.__new__(eb.EditBlockCoder)
        dummy.io = FakeIO()
        dummy.fence = ("```", "```")
        dummy.abs_root_path = lambda path: path
        failed = [("dummy.py", original, updated)]
        passed = []
        message = dummy._build_failed_edit_error_message(failed, passed)
        self.assertIn(
            "Warning: The REPLACE block content already exists in dummy.py.\nPlease confirm if the SEARCH/REPLACE block is still needed.",
            message
        )
        
if __name__ == "__main__":
    unittest.main()
    def test_diff_match_patch_significant_inaccuracy(self):
        """Test that a significant inaccuracy, such as a misspelling, is rejected."""
        whole = "def process_data(data, options):\n    return data.process(options)\n"
        # Introduce a severe error: misspelling 'process' as 'proccess' and missing comma
        part = "def proccess_data(data options):\n    return data.process(options)\n"
        replace = "def process_data(data, options):\n    return data.transform(options)\n"
        with self.assertRaises(ValueError):
            eb.replace_most_similar_chunk(whole, part, replace)
