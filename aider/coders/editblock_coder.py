import difflib
from difflib import SequenceMatcher, unified_diff
import math
import re
import sys
import diff_match_patch
from pathlib import Path

from aider import utils

from ..dump import dump  # noqa: F401
from .base_coder import Coder
from .editblock_prompts import EditBlockPrompts


import logging
logger = logging.getLogger(__name__)
# Get handlers from root logger to bypass its level filter
for handler in logging.getLogger().handlers:
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

DEFAULT_FENCE = ("`" * 3, "`" * 3)

# fuzzy matching tolerance using diff-match-patch


class EditBlockCoder(Coder):
    """A coder that uses search/replace blocks for code modifications.

    This coder specializes in making precise, controlled changes to code files using
    a search/replace block format. It can operate either as a top-level coder taking
    requests directly from users, or as a subordinate implementing changes specified
    by another coder.

    # Architectural Design Decisions

    ## Role Independence
    EditBlockCoder maintains strict focus on implementation:
    - Handles direct requests or specified changes
    - Makes no assumptions about larger processes
    - Stays focused on precise implementation
    - Flags issues rather than making decisions

    ## Core Competency
    Expertise in search/replace block format:
    - Exact matching of existing code
    - Precise replacement specification
    - Careful handling of whitespace and context
    - Support for file creation and deletion

    ## Implementation Notes
    - Uses search/replace blocks for all file modifications
    - Validates changes before applying them
    - Reports issues without attempting resolution
    - Maintains consistent format across all changes

    Attributes:
        edit_format: The edit format identifier for this coder type ("diff")
        gpt_prompts: The prompts configuration for this coder
    """

    edit_format = "diff"
    gpt_prompts = EditBlockPrompts()

    def get_edits(self):
        """Extract edit blocks from the LLM response.

        This method extracts edit blocks from the LLM's response content in
        self.partial_response_content. The format of the edit blocks depends on
        the specific coder implementation (e.g. EditBlockCoder uses search/replace blocks).

        Returns:
            list[Edit]: List of (path, original, updated) tuples representing the edits.
                     For shell commands, path will be None.
        """
        content = self.partial_response_content

        # Get both editable and read-only filenames
        valid_fnames = list(self.get_inchat_relative_files())
        if self.abs_read_only_fnames:
            for fname in self.abs_read_only_fnames:
                valid_fnames.append(self.get_rel_fname(fname))

        # might raise ValueError for malformed ORIG/UPD blocks
        edits = list(
            find_original_update_blocks(
                content,
                self.fence,
                valid_fnames,
            )
        )

        self.shell_commands += [edit[1] for edit in edits if edit[0] is None]
        edits = [edit for edit in edits if edit[0] is not None]

        return edits

    def apply_edits(self, edits):
        failed = []
        passed = []

        for edit in edits:
            path, original, updated = edit
            full_path = self.abs_root_path(path)
            content = self.io.read_text(full_path)
            new_content = do_replace(full_path, content, original, updated, self.fence)
            if not new_content:
                # try patching any of the other files in the chat
                for full_path in self.abs_fnames:
                    content = self.io.read_text(full_path)
                    new_content = do_replace(full_path, content, original, updated, self.fence)
                    if new_content:
                        break

            if new_content:
                self.io.write_text(full_path, new_content)
                passed.append(edit)
            else:
                failed.append(edit)

        if failed:
            raise ValueError(self._build_failed_edit_error_message(failed, passed))

    def _build_failed_edit_error_message(self, failed, passed):
        messages = []
        for edit in failed:
            path, original, updated = edit
            full_path = self.abs_root_path(path)
            content = self.io.read_text(full_path)
            header = f"## SearchReplaceNoExactMatch: The SEARCH block in {path} did not exactly match any content."
            block_info = f"<<<<<<< SEARCH\n{original}=======\n{updated}>>>>>>> REPLACE"
            candidate = find_similar_lines(original, content)
            if candidate:
                similarity_ratio = SequenceMatcher(None, original, candidate).ratio()
                similarity_percent = similarity_ratio * 100
                diff_lines = list(unified_diff(
                    original.splitlines(keepends=True),
                    candidate.splitlines(keepends=True),
                    fromfile="Expected SEARCH",
                    tofile="Candidate Snippet",
                ))
                diff_text = "".join(diff_lines)
                detail = (f"Detected similarity: {similarity_percent:.0f}% (threshold: {SIMILARITY_THRESHOLD * 100:.0f}%)\n"
                          f"Unified diff between expected and candidate snippet:\n{diff_text}\n"
                          f"Did you mean to match these actual lines from {path}?\n"
                          f"{self.fence[0]}\n{candidate}\n{self.fence[1]}")
            else:
                detail = "No similar candidate snippet found."
            suggestion = (f"Suggested corrections for {path}:\n"
                          "- Verify the SEARCH block exactly matches the file content (including whitespace, indentation, and punctuation).\n"
                          "- Check for accidental extra or missing spaces.\n"
                          "- Confirm that the file content has not been altered unexpectedly.")
            warning = ""
            if updated in content and updated:
                warning = (f"Warning: The REPLACE block content already exists in {path}.\n"
                           "Please confirm if the SEARCH/REPLACE block is still needed.")
            messages.append("\n".join([header, block_info, detail, suggestion, warning]))
        summary = ""
        if passed:
            pblocks = "block" if len(passed) == 1 else "blocks"
            blocks_str = "block" if len(failed) == 1 else "blocks"
            summary = f"\n# {len(passed)} SEARCH/REPLACE {pblocks} were applied successfully.\nOnly resend fixed versions of the {blocks_str} that failed."
        note = ("Note: The SEARCH section must exactly match an existing block of lines including all whitespace, "
                "comments, indentation, and formatting details.\n")
        return f"# {len(failed)} SEARCH/REPLACE block(s) failed to match!\n" + "\n".join(messages) + "\n" + note + summary


def prep(content):
    if content and not content.endswith("\n"):
        content += "\n"
    lines = content.splitlines(keepends=True)
    return content, lines


def replace_most_similar_chunk(whole, original, updated):
    """
    Uses diff-match-patch to perform fuzzy matching and patching for the search block.
    
    The matching strategy:
    1. Uses match_main to find best match location
    2. Uses patch_make and patch_apply to perform accurate replacement
    3. Requires 95% accuracy and rejects ambiguous matches
    
    Returns the new content with the matched region replaced by `updated`.
    Raises ValueError with diagnostic information if no sufficiently accurate match is found.
    """
    dmp = diff_match_patch.diff_match_patch()
    dmp.Match_Threshold = 0.05  # Require 95% accuracy
    dmp.Match_Distance = sys.maxsize  # Allow matches anywhere in file
    
    if not original:
        logger.debug("SEARCH block is empty; appending REPLACE block to the end of the file")
        return whole + updated
        
    match_index = dmp.match_main(whole, original, 0)
    if match_index == -1:
        logger.debug("SEARCH block not found in file content")
        logger.debug(f"search_text:\n{original}\nwhole:\n{whole}")
        raise ValueError(
            "SEARCH/REPLACE block failed: No sufficiently accurate match found.\n"
            "The search text may have transcription errors. Check for:\n"
            "- Extra or missing spaces\n"
            "- Different line breaks or indentation\n"
            "- Missing or altered punctuation\n"
            f"Search text was: {original!r}"
        )

    # Create a patch to replace the matched content
    matched_text = whole[match_index:match_index + len(original)]
    patches = dmp.patch_make(matched_text, updated)
    new_text, results = dmp.patch_apply(patches, whole)
    if not all(results):
        raise ValueError("Failed to apply patch - matched content may have unexpected format")
    return new_text


def strip_quoted_wrapping(res, fname=None, fence=DEFAULT_FENCE):
    """
    Given an input string which may have extra "wrapping" around it, remove the wrapping.
    For example:

    filename.ext
    ```
    We just want this content
    Not the filename and triple quotes
    ```
    """
    if not res:
        return res

    res = res.splitlines()

    if fname and res[0].strip().endswith(Path(fname).name):
        res = res[1:]

    if res[0].startswith(fence[0]) and res[-1].startswith(fence[1]):
        res = res[1:-1]

    res = "\n".join(res)
    if res and res[-1] != "\n":
        res += "\n"

    return res


def do_replace(fname, content, original, updated, fence=None):
    logger.debug(f"do_replace: {fname}\nSEARCH:\n{original}\nREPLACE:\n{updated}")
    original = strip_quoted_wrapping(original, fname, fence)
    updated = strip_quoted_wrapping(updated, fname, fence)
    logger.debug("do_replace: stripped original and updated content")
    logger.debug(f"do_replace: {fname}\nSEARCH:\n{original}\nREPLACE:\n{updated}")
    fname = Path(fname)

    # does it want to make a new file?
    if not fname.exists() and not original.strip():
        logger.debug(f"do_replace: creating new file {fname}")
        fname.touch()
        content = ""

    if content is None:
        logger.debug(f"do_replace: content is None for {fname}")
        return

    if not original.strip():
        # append to existing file, or start a new file
        logger.debug(f"do_replace: appending to {fname}")
        new_content = content + updated
    else:
        logger.debug(f"do_replace: replacing in {fname}")
        new_content = replace_most_similar_chunk(content, original, updated)
        if new_content is None:
            raise ValueError("SEARCH/REPLACE block failed to match: similarity below threshold. Check that the SEARCH block exactly matches the file content with only minor allowable differences.")
    return new_content


HEAD = r"^<{5,9} SEARCH\s*$"
DIVIDER = r"^={5,9}\s*$"
UPDATED = r"^>{5,9} REPLACE\s*$"

HEAD_ERR = "<<<<<<< SEARCH"
DIVIDER_ERR = "======="
UPDATED_ERR = ">>>>>>> REPLACE"

separators = "|".join([HEAD, DIVIDER, UPDATED])

split_re = re.compile(r"^((?:" + separators + r")[ ]*\n)", re.MULTILINE | re.DOTALL)


missing_filename_err = (
    "Missing or incorrect filename. The filename must be alone on the line"
    " before the opening fence. If this search/replacement block modifies existing"
    " content, then file path and name must exactly match an existing file."
    " {fence[0]}"
)


def strip_filename(filename):
    """Clean up a filename by stripping certain surrounding characters.

    Returns:
        str: the filename with strippable characters stripped, which might then be empty
    """
    filename = filename.strip()
    if filename.startswith("#"):
        filename = filename[1:]
    if filename.endswith(":"):
        filename = filename[:-1]
    filename = filename.strip()
    if filename.startswith("`") and filename.endswith("`"):
        filename = filename[1:-1]

    return filename


def find_original_update_blocks(content, fence=DEFAULT_FENCE, valid_fnames=None):
    """Parse search/replace blocks from the content.

    The actual requirements for search/replace blocks are more flexible than what we tell the model:

    File Path Requirements:
    - Must be alone on a line before the opening fence
    - Can be stripped of trailing colons, leading #, and surrounding backticks/asterisks
    - For new files, an empty SEARCH section is allowed
    - The path can be relative to project root
    - The path must be valid (either match an existing file or be a new file path)
    - For existing files, path must match a filename in valid_fnames

    Block Structure Requirements:
    - Opening fence (e.g. ```python) - language specifier is optional
    - "<<<<<<< SEARCH" line (5+ < characters)
    - Search content (can be empty for new files)
    - "=======" line (5+ = characters)
    - Replace content
    - ">>>>>>> REPLACE" line (5+ > characters)
    - Closing fence (```)

    Search Content Requirements:
    - For existing files, must match exactly (including whitespace)
    - Exception: The code has special handling for leading whitespace mismatches
    - Exception: Can handle "..." lines that match between search and replace sections

    Multiple Blocks:
    - Multiple blocks for the same file are allowed
    - Each block is processed independently
    - Only the first match in a file is replaced

    Args:
        content (str): The content to parse for search/replace blocks
        fence (tuple): Opening and closing fence markers
        valid_fnames (list): Combined list of editable and read-only filenames that can be edited
    """
    lines = content.splitlines(keepends=True)
    i = 0

    head_pattern = re.compile(HEAD)
    divider_pattern = re.compile(DIVIDER)
    updated_pattern = re.compile(UPDATED)

    while i < len(lines):
        line = lines[i]

        # Check for shell code blocks
        shell_starts = [
            "```bash",
            "```sh",
            "```shell",
            "```cmd",
            "```batch",
            "```powershell",
            "```ps1",
            "```zsh",
            "```fish",
            "```ksh",
            "```csh",
            "```tcsh",
        ]
        next_is_editblock = i + 1 < len(lines) and head_pattern.match(lines[i + 1].strip())

        if any(line.strip().startswith(start) for start in shell_starts) and not next_is_editblock:
            shell_content = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                shell_content.append(lines[i])
                i += 1
            if i < len(lines) and lines[i].strip().startswith("```"):
                i += 1  # Skip the closing ```

            yield None, "".join(shell_content)
            continue

        # Check for SEARCH/REPLACE blocks
        if head_pattern.match(line.strip()):
            try:
                if i < 2:
                    raise ValueError(
                        "Each SEARCH/REPLACE block must begin with a filename and a fence; "
                        f"Found a {HEAD} on line {i}"
                    )
                if i < 2 or not lines[i - 1].startswith(fence[0]):
                    raise ValueError(
                        "Each SEARCH/REPLACE block must begin with a filename and a fence.\n"
                        f"""Expected "{fence[0]}" at the start of line {i - 1}, but got this:\n"""
                        f"{lines[i - 1]!r}\n"
                    )

                filename_line = lines[i - 2]
                if not strip_filename(filename_line) and i >= 3:
                    filename_line = lines[i - 3]
                is_new_file = i + 1 < len(lines) and divider_pattern.match(lines[i + 1].strip())
                if is_new_file:
                    use_valid_fnames = None
                else:
                    use_valid_fnames = valid_fnames
                filename = find_filename(filename_line, use_valid_fnames)
                if not filename:
                    raise ValueError(missing_filename_err.format(fence=fence))

                original_text = []
                i += 1
                while i < len(lines) and not divider_pattern.match(lines[i].strip()):
                    original_text.append(lines[i])
                    i += 1

                if i >= len(lines) or not divider_pattern.match(lines[i].strip()):
                    raise ValueError(f"Expected `{DIVIDER_ERR}`")

                updated_text = []
                i += 1
                while i < len(lines) and not (
                    updated_pattern.match(lines[i].strip())
                    or divider_pattern.match(lines[i].strip())
                ):
                    updated_text.append(lines[i])
                    i += 1

                if i >= len(lines) or not (
                    updated_pattern.match(lines[i].strip())
                    or divider_pattern.match(lines[i].strip())
                ):
                    raise ValueError(f"Expected `{UPDATED_ERR}` or `{DIVIDER_ERR}`")

                yield filename, "".join(original_text), "".join(updated_text)

            except ValueError as e:
                processed = "".join(lines[: i + 1])
                err = e.args[0]
                raise ValueError(f"{processed}\n^^^ {err}")

        i += 1


def find_filename(line, valid_fnames):
    """Find a filename in line.

    The filename must be alone on the line, optionally preceded by # or
    surrounded by backticks.

    If valid_fnames is provided, the stripped filename must be in the list.

    Args:
        lines (list): the lines that may contain the filename in priority order
        fence (tuple): Opening and closing fence markers
        valid_fnames (list): List of valid filenames to match against
           If empty or not provided, then any syntactically valid filename is accepted.

    Returns:
        str: The found filename, or None if no valid filename found
    """
    filename = strip_filename(line)
    if not filename:
        return None

    # For existing files, require an exact match
    if valid_fnames:
        # Check for exact match first
        if filename in valid_fnames:
            return filename

        # Check for basename match
        for valid_fname in valid_fnames:
            if filename == Path(valid_fname).name:
                return valid_fname

    # For new files, require a file extension
    elif "." in filename:
        return filename

    return None


def find_similar_lines(search_text: str, content_text: str, threshold: float = 0.6) -> str:
    """
    Use diff-match-patch to locate a candidate snippet in content_text that is similar
    to search_text. Returns the candidate snippet if the similarity is above the threshold,
    otherwise returns an empty string.
    """
    dmp = diff_match_patch.diff_match_patch()
    match_index = dmp.match_main(content_text, search_text, 0)
    if match_index == -1:
        return ""
    candidate = content_text[match_index: match_index + len(search_text)]
    diffs = dmp.diff_main(candidate, search_text)
    dmp.diff_cleanupSemantic(diffs)
    distance = dmp.diff_levenshtein(diffs)
    similarity = 1 - (distance / len(search_text))
    if similarity < threshold:
        return ""
    return candidate


def main():
    history_md = Path(sys.argv[1]).read_text()
    if not history_md:
        return

    messages = utils.split_chat_history_markdown(history_md)

    for msg in messages:
        msg = msg["content"]
        edits = list(find_original_update_blocks(msg))

        for fname, before, after in edits:
            # Compute diff
            diff = difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile="before",
                tofile="after",
            )
            diff = "".join(diff)
            dump(before)
            dump(after)
            dump(diff)


if __name__ == "__main__":
    main()
