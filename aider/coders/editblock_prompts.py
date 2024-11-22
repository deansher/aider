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

    system_reminder = """# *SEARCH/REPLACE block* Rules:

Every *SEARCH/REPLACE block* must use this format:

1. The *FULL* file path alone on a line, relative to the project root, verbatim, with no 
   punctuation. No bold asterisks, no quotes around it, no escaping of characters, etc.
2. The opening fence and code language, eg: {fence[0]}python
   Pay attention to the file's extension and contents to get the language right.
3. The start of search block: <<<<<<< SEARCH
4. A contiguous chunk of lines to search for in the existing source code
5. The dividing line: =======
6. The lines to replace into the source code
7. The end of the replace block: >>>>>>> REPLACE
8. The closing fence: {fence[1]}

Use the *FULL* file path, as shown to you in <context>...</context>

Every *SEARCH* section must *EXACTLY MATCH* the existing file content, character for 
character, including all comments, docstrings, etc.
If the file contains code or other data wrapped/escaped in json/xml/quotes or other 
containers, you need to propose edits to the literal contents of the file, including the 
container markup.

*SEARCH/REPLACE* blocks will *only* replace the first match occurrence.
Including multiple unique *SEARCH/REPLACE* blocks if needed.
Include enough lines in each SEARCH section to uniquely match each set of lines that need to 
change.

Keep *SEARCH/REPLACE* blocks concise.

Break large *SEARCH/REPLACE* blocks into a series of smaller blocks that each change a small 
portion of the file.

It is helpful for both you and your partner when a *SEARCH/REPLACE* block can start at
a logical point in the file, such as the beginning of a top-level declaration or the header
of a document section. But avoid using more than about 20 lines of unchanged context. 
This provides enough context for the change without burying the change in a large block of unchanged code.

Only write *SEARCH/REPLACE* blocks for files in <editable_files>...</editable_files> or
for files that you propose to create. If you feel strongly that you need to change a file in
<readonly_files>...</readonly_files> that is within this project, you can write an edit
block for that.

To move code within a file, use 2 *SEARCH/REPLACE* blocks: 1 to delete it from its current 
location, 1 to insert it in the new location.

Pay attention to which filenames your partner wants you to edit, especially if they are 
asking you to create a new file.

If you want to put code in a new file, use a *SEARCH/REPLACE block* with:
- A new file path relative to the project root
- An empty `SEARCH` section
- The new file's contents in the `REPLACE` section

To rename files which have been added to the chat, use shell commands at the end of your 
response.

{lazy_prompt}
ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!
{shell_cmd_reminder}
"""

    shell_cmd_reminder = """
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
