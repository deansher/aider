# flake8: noqa: E501

import tempfile
import unittest
from pathlib import Path

from aider.coders import Coder
from aider.coders import editblock_coder as eb
from aider.io import InputOutput
from aider.models import _ModelConfigImpl


class TestUtils(unittest.TestCase):
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

    def test_replace_most_similar_chunk(self):
        whole = (
            "def compute_sum(numbers):\n"
            "    total = 0\n"
            "    for num in numbers:\n"
            "        total += num\n"
            "    return total\n"
        )
        part = (
            "def compute_sum(numbers):\n"
            "    total = 1  # Wrong initialization\n"
            "    for num in numbers\n"
            "        total *= num  # Wrong operation\n"
            "    return total + 1  # Wrong return\n"
        )
        replace = (
            "def compute_sum(numbers):\n"
            "    return sum(numbers)\n"
        )
        with self.assertRaises(ValueError):
             eb.replace_most_similar_chunk(whole, part, replace)

    # fuzzy logic disabled v0.11.2-dev
    def test_replace_most_similar_chunk_not_perfect_match(self):
        whole = (
            "def compute_sum(numbers):\n"
            "    total = 0\n"
            "    for num in numbers:\n"
            "        total += num\n"
            "    return total\n"
        )
        part = (
            "def compute_sum(numbers):\n"
            "    total = 0\n"
            "    for num in numbers:\n"
            "        total = total * 2  # Different logic\n"
            "    return total\n"
        )
        replace = (
            "def compute_sum(numbers):\n"
            "    return sum(numbers)\n"
        )

        with self.assertRaises(ValueError):
             eb.replace_most_similar_chunk(whole, part, replace)

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
            "    total += num\n"
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

    def test_replace_part_with_missing_varied_leading_whitespace(self):
        whole = (
            "\n"
            "    line1\n"
            "    line2\n"
            "        line3\n"
            "    line4\n"
        )

        part = "line2\n    line3\n"
        replace = "new_line2\n    new_line3\n"
        expected_output = (
            "\n"
            "    line1\n"
            "    new_line2\n"
            "        new_line3\n"
            "    line4\n"
        )

        with self.assertRaises(ValueError):
             eb.replace_most_similar_chunk(whole, part, replace)


    def test_replace_part_with_missing_leading_whitespace(self):
        whole = (
            "    line1\n"
            "    line2\n"
            "    line3\n"
        )
        part = (
            "line1\n"
            "line2\n"
        )
        replace = (
            "new_line1\n"
            "new_line2\n"
        )
        expected_output = (
            "    new_line1\n"
            "    new_line2\n"
            "    line3\n"
        )

        result = eb.replace_most_similar_chunk(whole, part, replace)  
        self.assertEqual(result, expected_output)

    def test_replace_multiple_matches(self):
        """Test successful exact match replacement.
        
        This test verifies that when the search text exactly matches a portion of the content:
        1. The replacement succeeds (similarity = 1.0, well above our 0.95 threshold)
        2. Only the first occurrence is replaced
        """
        whole = (
            "def foo():\n    return 42\n\n"
            "def bar():\n    return 43\n\n"
            "def foo():\n    return 44\n"
        )
        part = "def foo():\n    return 42\n"
        replace = "def foo():\n    return 100\n"
        expected_output = (
            "def foo():\n    return 100\n\n"
            "def bar():\n    return 43\n\n"
            "def foo():\n    return 44\n"
        )

        result = eb.replace_most_similar_chunk(whole, part, replace)
        self.assertEqual(result, expected_output)
        
    def test_replace_multiple_matches_missing_whitespace(self):
        "only replace first occurrence"

        whole = (
            "    def bar():\n        return 42\n\n"
            "    def baz():\n        return 43\n\n"
            "    def bar():\n        return 44\n"
        )
        part = "def bar():\n    return 42\n"
        replace = "def bar():\n    return 100\n"
        expected_output = (
            "    def bar():\n        return 100\n\n"
            "    def baz():\n        return 43\n\n"
            "    def bar():\n        return 44\n"
        )

        result = eb.replace_most_similar_chunk(whole, part, replace)
        self.assertEqual(result, expected_output)

    def test_replace_part_with_just_some_missing_leading_whitespace(self):
        whole = "    line1\n    line2\n    line3\n"
        part = " line1\n line2\n"
        replace = " new_line1\n     new_line2\n"
        expected_output = "    new_line1\n        new_line2\n    line3\n"

        result = eb.replace_most_similar_chunk(whole, part, replace)
        self.assertEqual(result, expected_output)

    def test_replace_part_with_some_missing_leading_whitespace(self):
        whole = (
            "    def baz(x):\n"
            "        if x > 0:\n"
            "            return x\n"
        )
        part = (
            "def baz(x):\n"
            "    if x > 0:\n"
            "        return x\n"
        )
        replace = (
            "def baz(x):\n"
            "    if x >= 0:\n"
            "        return x + 1\n"
        )
        expected_output = (
            "    def baz(x):\n"
            "        if x >= 0:\n"
            "            return x + 1\n"
        )

        result = eb.replace_most_similar_chunk(whole, part, replace)
        self.assertEqual(result, expected_output)

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


# New tests for diff-match-patch integration

def test_diff_match_patch_minor_inaccuracy():
    """Test that even minor differences trigger a failure when similarity falls below 0.95.
    
    This test verifies our strict matching requirements:
    1. A missing comma produces a similarity score around 0.85
    2. Since 0.85 < 0.95 (our threshold), this should raise a ValueError
    3. This enforces our design decision to require near-exact matches
    """
    whole = "Hello, world!\n"
    part = "Hello world!\n"  # missing comma
    replace = "Hi, world!\n"
    
    with pytest.raises(ValueError) as excinfo:
        eb.replace_most_similar_chunk(whole, part, replace)
    assert "SEARCH/REPLACE block failed" in str(excinfo.value)

def test_diff_match_patch_significant_mismatch():
    """
    Test that when the search text is significantly different from the target content,
    the diff-match-patch based matching raises a ValueError.
    """
    import pytest
    whole = "This is a completely different text.\n"
    part = "Hello, world!\n"
    replace = "Hi, world!\n"
    with pytest.raises(ValueError) as excinfo:
         eb.replace_most_similar_chunk(whole, part, replace)
    assert "SEARCH/REPLACE block failed" in str(excinfo.value)

if __name__ == "__main__":
    unittest.main()
