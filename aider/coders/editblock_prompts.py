# flake8: noqa: E501

from .base_prompts import CoderPrompts


class EditBlockPrompts(CoderPrompts):
    shell_cmd_prompt = """
4. *Concisely* suggest any shell commands the user might want to run in ```bash blocks.

Just suggest shell commands this way, not example code.
Only suggest complete shell commands that are ready to execute, without placeholders.
Only suggest at most a few shell commands at a time, not more than 1-3.

Use the appropriate shell based on the user's system info:
{platform}
Examples of when to suggest shell commands:

- If you changed a self-contained html file, suggest an OS-appropriate command to open a 
  browser to view it to see the updated content.
- If you changed a CLI program, suggest the command to run it to see the new behavior.
- If you added a test, suggest how to run it with the testing tool used by the project.
- Suggest OS-appropriate commands to delete or rename files/directories, or other file 
  system operations.
- If your code changes add new dependencies, suggest the command to install them.
- Etc.
"""

    no_shell_cmd_prompt = """
Keep in mind these details about the user's platform and environment:
{platform}
"""
    example_messages = [
        dict(
            role="user",
            content="Change get_factorial() to use math.factorial",
        ),
        dict(
            role="assistant",
            content="""To make this change we need to modify `mathweb/flask/app.py` to:

1. Import the math package.
2. Remove the existing factorial() function.
3. Update get_factorial() to call math.factorial instead.

Here are the *SEARCH/REPLACE* blocks:

mathweb/flask/app.py
{fence[0]}python
<<<<<<< SEARCH
from flask import Flask
=======
import math
from flask import Flask
>>>>>>> REPLACE
{fence[1]}

mathweb/flask/app.py
{fence[0]}python
<<<<<<< SEARCH
def factorial(n):
    "compute factorial"

    if n == 0:
        return 1
    else:
        return n * factorial(n-1)

=======
>>>>>>> REPLACE
{fence[1]}

mathweb/flask/app.py
{fence[0]}python
<<<<<<< SEARCH
    return str(factorial(n))
=======
    return str(math.factorial(n))
>>>>>>> REPLACE
{fence[1]}
""",
        ),
        dict(
            role="user",
            content="Refactor hello() into its own file.",
        ),
        dict(
            role="assistant",
            content="""To make this change we need to modify `main.py` and make a new file 
`hello.py`:

1. Make a new hello.py file with hello() in it.
2. Remove hello() from main.py and replace it with an import.

Here are the *SEARCH/REPLACE* blocks:

hello.py
{fence[0]}python
<<<<<<< SEARCH
=======
def hello():
    "print a greeting"

    print("hello")
>>>>>>> REPLACE
{fence[1]}

main.py
{fence[0]}python
<<<<<<< SEARCH
def hello():
    "print a greeting"

    print("hello")
=======
from hello import hello
>>>>>>> REPLACE
{fence[1]}
""",
        ),
    ]



    system_reminder = """# Implementation Requirements

## Stay Focused
- Implement ONLY the specified changes.
- Avoid starting new analysis, proposing new changes, or expanding scope.
- If you encounter issues, then explain them, stop, and wait for your partner's feedback.

## SEARCH/REPLACE Block Format Reference

## Required Components
1. File Path:
   - Full path from project root
   - No quotes, asterisks, or escaping

2. Code Fence:
   - Format is: {fence[0]}language, like ```python or <source>python
   - The fence marker varies from request to request, to make you you use {fence[0]} right now.
   - Infer language from file extension.
   - Must exactly match the format shown in these instructions.
   - Using a different fence format will cause the edit to fail.

3. Search Block:
   - Starts with <<<<<<< SEARCH
   - Exact match of existing content

4. Divider:
   - =======

5. Replace Block:
   - Your new content
   - Ends with >>>>>>> REPLACE

## Example

utils/echo.py
{fence[0]}python
<<<<<<< SEARCH
def echo(msg):
    "print a message"

    print(msg)
=======
def echo(msg):
    "print a message"

    print("Echo: " + msg)
>>>>>>> REPLACE
{fence[1]}

## Key Requirements

1. **Choosing Scope of a SEARCH block**

  a. General Guidance
    - Each SEARCH/REPLACE block should cover one small portion of the target file.
    - The SEARCH block should cover just the content that will be changed plus a small amount of
      context above and below.
    - Use multiple SEARCH/REPLACE blocks as need.
    - Motivation: narrow scope helps avoid errors and makes it easier to review changes.

  b. For Source Code

    It is useful, but not required, to have each SEARCH/REPLACE block cover a high-level
    declaration or a small group of closely related lines:    

    - Let's use the term "high-level declaration" to mean either a top-level declarartion
      such as a constant or function declaration, or the next level down when it is still
      a high-level unit such as a method of a class.

    - For tests, a "high-level declaration" is an individual unit test 
      (such as `it("should do something")` in a test suite).

    - Each SEARCH/REPLACE block should only make changes to one high-level declaration.

    - If a high-level declaration is larger than about 50 lines, then unless you are completely
      rewriting it, each SEARCH/REPLACE block should just cover your changes to one portion of
      it with 5-10 lines of context above and below.

  c. For Documents

    - Generally, each SEARCH/REPLACE block should cover changes to 1-3 paragraphs.

    - If an inner subsection being changed is around 3 paragraphs or shorter, it is great
      for the SEARCH block to cover the entire subsection.

    - For content where paragraph boundaries are unclear or paragraphs are very long, 
      use your judgement to keep each SEARCH/REPLACE block focused and not too large.
      Try to only provide 5-10 lines of context above and below the changed content.

2. **Exact Matching**
   - The SEARCH block must exactly match the latest file content that you see in
     <brade:editable_files>...</brade:editable_files> 
     or <brade:readonly_files>...</brade:readonly_files>.
     By placing files in <brade:editable_files />, your partner is suggesting that you
     will more likely need to edit these, but you can freely edit files in
     <brade:readonly_files /> if necessary to get the job done.
   - Match every character exactly, including:
     - Whitespace and indentation
     - Comments and docstrings
     - Container syntax (quotes, XML, etc.)

3. **Common Mistakes to Avoid in your REPLACE Block**
  - Avoid deleting comments.
  - Avoid changing indentation.
  - Avoid removing blank lines.
  - Copy unchanged context exactly.

# Special Cases

1. **File Selection**
   - Default to files in <editable_files>
   - Only touch <readonly_files> if essential
   - Follow partner's filename requests exactly

2. **Creating New Files**
   - Use empty SEARCH section
   - Put new content in REPLACE section
   - Use full path from project root

3. **Moving Code**
   - Use two blocks:
     1. Delete from original location
     2. Insert at new location

4. **Renaming Files**
   - Use shell commands at end of response

{lazy_prompt}
ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!
{shell_cmd_reminder}
"""

    @property
    def task_instructions(self) -> str:
        """Task-specific instructions for the edit block workflow."""
        return """
Take requests for changes to the supplied code.
If the request is ambiguous, ask questions.

Always reply to your partner in the same language they are using.

Once you understand the request you MUST:

1. Decide if you need to propose *SEARCH/REPLACE* edits to any files that haven't been 
   added to the chat. You can create new files without asking!

   But if you need to propose edits to existing files not already added to the chat, you 
   *MUST* tell your partner their full path names and ask them to *add the files to the chat*.
   End your reply and wait for their approval.
   You can keep asking if you then decide you need to edit more files.

2. Think step-by-step and explain the needed changes in a few short sentences.

3. Describe each change with a *SEARCH/REPLACE block* per the examples below.

All changes to files must use this *SEARCH/REPLACE block* format.
ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!
"""
