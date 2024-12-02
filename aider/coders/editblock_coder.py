import difflib
import math
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from aider import utils

from ..dump import dump  # noqa: F401
from .base_coder import Coder
from .editblock_prompts import EditBlockPrompts


class EditBlockCoder(Coder):
    """A coder that uses search/replace blocks for code modifications."""

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

        if not failed:
            return

        blocks = "block" if len(failed) == 1 else "blocks"

        res = f"# {len(failed)} SEARCH/REPLACE {blocks} failed to match!\n"
        for edit in failed:
            path, original, updated = edit

            full_path = self.abs_root_path(path)
            content = self.io.read_text(full_path)

            res += f"""
## SearchReplaceNoExactMatch: This SEARCH block failed to exactly match lines in {path}
<<<<<<< SEARCH
{original}=======
{updated}>>>>>>> REPLACE

"""
            did_you_mean = find_similar_lines(original, content)
            if did_you_mean:
                res += f"""Did you mean to match some of these actual lines from {path}?

{self.fence[0]}
{did_you_mean}
{self.fence[1]}

"""

            if updated in content and updated:
                res += f"""Are you sure you need this SEARCH/REPLACE block?
The REPLACE lines are already in {path}!

"""
        res += (
            "The SEARCH section must exactly match an existing block of lines including all white"
            " space, comments, indentation, docstrings, etc\n"
        )
        if passed:
            pblocks = "block" if len(passed) == 1 else "blocks"
            res += f"""
# The other {len(passed)} SEARCH/REPLACE {pblocks} were applied successfully.
Don't re-send them.
Just reply with fixed versions of the {blocks} above that failed to match.
"""
        raise ValueError(res)


def prep(content):
    if content and not content.endswith("\n"):
        content += "\n"
    lines = content.splitlines(keepends=True)
    return content, lines


def perfect_or_whitespace(whole_lines, part_lines, replace_lines):
    # Try for a perfect match
    res = perfect_replace(whole_lines, part_lines, replace_lines)
    if res:
        return res

    # Try being flexible about leading whitespace
    res = replace_part_with_missing_leading_whitespace(whole_lines, part_lines, replace_lines)
    if res:
        return res


def perfect_replace(whole_lines, part_lines, replace_lines):
    part_tup = tuple(part_lines)
    part_len = len(part_lines)

    for i in range(len(whole_lines) - part_len + 1):
        whole_tup = tuple(whole_lines[i : i + part_len])
        if part_tup == whole_tup:
            res = whole_lines[:i] + replace_lines + whole_lines[i + part_len :]
            return "".join(res)


def replace_most_similar_chunk(whole, part, replace):
    """Best efforts to find the `part` lines in `whole` and replace them with `replace`.

    The code is more flexible than what we tell the model about matching:

    1. Perfect match - tries for exact character-by-character match first

    2. Whitespace flexibility:
    - Handles mismatched leading whitespace
    - Can match content with different indentation levels

    3. Elided content with "...":
    - Supports matching across elided sections marked with ...
    - The ... must match exactly between search and replace sections
    - The non-elided chunks must match exactly

    4. Empty search sections:
    - Allowed for new files
    - Results in appending content to existing files
    """

    whole, whole_lines = prep(whole)
    part, part_lines = prep(part)
    replace, replace_lines = prep(replace)

    res = perfect_or_whitespace(whole_lines, part_lines, replace_lines)
    if res:
        return res

    # drop leading empty line, GPT sometimes adds them spuriously (issue #25)
    if len(part_lines) > 2 and not part_lines[0].strip():
        skip_blank_line_part_lines = part_lines[1:]
        res = perfect_or_whitespace(whole_lines, skip_blank_line_part_lines, replace_lines)
        if res:
            return res

    # Try to handle when it elides code with ...
    try:
        res = try_dotdotdots(whole, part, replace)
        if res:
            return res
    except ValueError:
        pass

    return
    # Try fuzzy matching
    res = replace_closest_edit_distance(whole_lines, part, part_lines, replace_lines)
    if res:
        return res


def try_dotdotdots(whole, part, replace):
    """
    See if the edit block has ... lines.
    If not, return none.

    If yes, try and do a perfect edit with the ... chunks.
    If there's a mismatch or otherwise imperfect edit, raise ValueError.

    If perfect edit succeeds, return the updated whole.
    """

    dots_re = re.compile(r"(^\s*\.\.\.\n)", re.MULTILINE | re.DOTALL)

    part_pieces = re.split(dots_re, part)
    replace_pieces = re.split(dots_re, replace)

    if len(part_pieces) != len(replace_pieces):
        raise ValueError("Unpaired ... in SEARCH/REPLACE block")

    if len(part_pieces) == 1:
        # no dots in this edit block, just return None
        return

    # Compare odd strings in part_pieces and replace_pieces
    all_dots_match = all(part_pieces[i] == replace_pieces[i] for i in range(1, len(part_pieces), 2))

    if not all_dots_match:
        raise ValueError("Unmatched ... in SEARCH/REPLACE block")

    part_pieces = [part_pieces[i] for i in range(0, len(part_pieces), 2)]
    replace_pieces = [replace_pieces[i] for i in range(0, len(replace_pieces), 2)]

    pairs = zip(part_pieces, replace_pieces)
    for part, replace in pairs:
        if not part and not replace:
            continue

        if not part and replace:
            if not whole.endswith("\n"):
                whole += "\n"
            whole += replace
            continue

        if whole.count(part) == 0:
            raise ValueError
        if whole.count(part) > 1:
            raise ValueError

        whole = whole.replace(part, replace, 1)

    return whole


def replace_part_with_missing_leading_whitespace(whole_lines, part_lines, replace_lines):
    # GPT often messes up leading whitespace.
    # It usually does it uniformly across the ORIG and UPD blocks.
    # Either omitting all leading whitespace, or including only some of it.

    # Outdent everything in part_lines and replace_lines by the max fixed amount possible
    leading = [len(p) - len(p.lstrip()) for p in part_lines if p.strip()] + [
        len(p) - len(p.lstrip()) for p in replace_lines if p.strip()
    ]

    if leading and min(leading):
        num_leading = min(leading)
        part_lines = [p[num_leading:] if p.strip() else p for p in part_lines]
        replace_lines = [p[num_leading:] if p.strip() else p for p in replace_lines]

    # can we find an exact match not including the leading whitespace
    num_part_lines = len(part_lines)

    for i in range(len(whole_lines) - num_part_lines + 1):
        add_leading = match_but_for_leading_whitespace(
            whole_lines[i : i + num_part_lines], part_lines
        )

        if add_leading is None:
            continue

        replace_lines = [add_leading + rline if rline.strip() else rline for rline in replace_lines]
        whole_lines = whole_lines[:i] + replace_lines + whole_lines[i + num_part_lines :]
        return "".join(whole_lines)

    return None


def match_but_for_leading_whitespace(whole_lines, part_lines):
    num = len(whole_lines)

    # does the non-whitespace all agree?
    if not all(whole_lines[i].lstrip() == part_lines[i].lstrip() for i in range(num)):
        return

    # are they all offset the same?
    add = set(
        whole_lines[i][: len(whole_lines[i]) - len(part_lines[i])]
        for i in range(num)
        if whole_lines[i].strip()
    )

    if len(add) != 1:
        return

    return add.pop()


def replace_closest_edit_distance(whole_lines, part, part_lines, replace_lines):
    similarity_thresh = 0.8

    max_similarity = 0
    most_similar_chunk_start = -1
    most_similar_chunk_end = -1

    scale = 0.1
    min_len = math.floor(len(part_lines) * (1 - scale))
    max_len = math.ceil(len(part_lines) * (1 + scale))

    for length in range(min_len, max_len):
        for i in range(len(whole_lines) - length + 1):
            chunk = whole_lines[i : i + length]
            chunk = "".join(chunk)

            similarity = SequenceMatcher(None, chunk, part).ratio()

            if similarity > max_similarity and similarity:
                max_similarity = similarity
                most_similar_chunk_start = i
                most_similar_chunk_end = i + length

    if max_similarity < similarity_thresh:
        return

    modified_whole = (
        whole_lines[:most_similar_chunk_start]
        + replace_lines
        + whole_lines[most_similar_chunk_end:]
    )
    modified_whole = "".join(modified_whole)

    return modified_whole


DEFAULT_FENCE = ("`" * 3, "`" * 3)


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


def do_replace(fname, content, before_text, after_text, fence=None):
    before_text = strip_quoted_wrapping(before_text, fname, fence)
    after_text = strip_quoted_wrapping(after_text, fname, fence)
    fname = Path(fname)

    # does it want to make a new file?
    if not fname.exists() and not before_text.strip():
        fname.touch()
        content = ""

    if content is None:
        return

    if not before_text.strip():
        # append to existing file, or start a new file
        new_content = content + after_text
    else:
        new_content = replace_most_similar_chunk(content, before_text, after_text)

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
    "Bad/missing filename. The filename must be alone on the line before the opening fence"
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


def find_similar_lines(search_lines, content_lines, threshold=0.6):
    search_lines = search_lines.splitlines()
    content_lines = content_lines.splitlines()

    best_ratio = 0
    best_match = None

    for i in range(len(content_lines) - len(search_lines) + 1):
        chunk = content_lines[i : i + len(search_lines)]
        ratio = SequenceMatcher(None, search_lines, chunk).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = chunk
            best_match_i = i

    if best_ratio < threshold:
        return ""

    if best_match[0] == search_lines[0] and best_match[-1] == search_lines[-1]:
        return "\n".join(best_match)

    N = 5
    best_match_end = min(len(content_lines), best_match_i + len(search_lines) + N)
    best_match_i = max(0, best_match_i - N)

    best = content_lines[best_match_i:best_match_end]
    return "\n".join(best)


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
