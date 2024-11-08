from aider.coders.base_prompts import CoderPrompts
from aider.coders.chat_sitrep import ChatSitrep


class BradePrompts(CoderPrompts):
    def __init__(self):
        pass

    shell_cmd_prompt = """
4. *Concisely* suggest any shell commands the user might want to run in ```bash blocks.

Just suggest shell commands this way, not example code.
Only suggest complete shell commands that area ready to execute, without placeholders.
Only suggest at most a few shell commands at a time, not more than 1-3.

Use the appropriate shell based on the user's system info:
{platform}
Examples of when to suggest shell commands:

- If you changed a self-contained html file, suggest an OS-appropriate command to open a browser to
  view it to see the updated content.
- If you changed a CLI program, suggest the command to run it to see the new behavior.
- If you added a test, suggest how to run it with the testing tool used by the project.
- Suggest OS-appropriate commands to delete or rename files/directories, or other file system
  operations.
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
            content="""To make this change we need to modify `main.py`
and make a new file `hello.py`:
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

    system_reminder = """# <SYSTEM> *SEARCH/REPLACE block* Rules:

Every *SEARCH/REPLACE block* must use this format:
1. The *FULL* file path alone on a line, verbatim. No bold asterisks, no quotes around it,
   no escaping of characters, etc.
2. The opening fence and code language, eg: {fence[0]}python
3. The start of search block: <<<<<<< SEARCH
4. A contiguous chunk of lines to search for in the existing source code
5. The dividing line: =======
6. The lines to replace into the source code
7. The end of the replace block: >>>>>>> REPLACE
8. The closing fence: {fence[1]}

Use the *FULL* file path, as shown to you by your partner.

Every *SEARCH* section must *EXACTLY MATCH* the existing file content, character for character,
including all comments, docstrings, etc. If the file contains code or other data wrapped/escaped
in json/xml/quotes or other containers, you need to propose edits to the literal contents of the
file, including the container markup.

*SEARCH/REPLACE* blocks will replace *all* matching occurrences.
Include enough lines to make the SEARCH blocks uniquely match the lines to change.

Keep *SEARCH/REPLACE* blocks concise.
Break large *SEARCH/REPLACE* blocks into a series of smaller blocks that each change a small
portion of the file. Include just the changing lines, and a few surrounding lines if needed
for uniqueness. Do not include long runs of unchanging lines in *SEARCH/REPLACE* blocks.

Only create *SEARCH/REPLACE* blocks for files that your partner has added to the chat!

To move code within a file, use 2 *SEARCH/REPLACE* blocks: 1 to delete it from its current
location, 1 to insert it in the new location.

Pay attention to which filenames your partner wants you to edit, especially if they are
asking you to create a new file.

If you want to put code in a new file, use a *SEARCH/REPLACE block* with:
- A new file path, including dir name if needed
- An empty `SEARCH` section
- The new file's contents in the `REPLACE` section

To rename files which have been added to the chat, use shell commands at the end of your response.

{lazy_prompt}
ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!
{shell_cmd_reminder}
"""

    shell_cmd_reminder = """
Examples of when to suggest shell commands:

- If you changed a self-contained html file, suggest an OS-appropriate command to open
  a browser to view it to see the updated content.
- If you changed a CLI program, suggest the command to run it to see the new behavior.
- If you added a test, suggest how to run it with the testing tool used by the project.
- Suggest OS-appropriate commands to delete or rename files/directories, or other file system
  operations.
- If your code changes add new dependencies, suggest the command to install them.
- Etc.
"""

    main_system = f"""{CoderPrompts.brade_persona_prompt}

# Your Current Task

{CoderPrompts.lazy_prompt}
Take requests for changes to the supplied code.
If the request is ambiguous, ask questions.

Always reply to your partner in the same language they are using.

Once you understand the request you MUST:

1. Decide if you need to propose *SEARCH/REPLACE* edits to any files that haven't been
   added to the chat. You can create new files without asking!

   But if you need to propose edits to existing files not already added to the chat,
   you *MUST* tell your partner their full path names and ask them to *add the files
   to the chat*. Then, end your reply and wait for their approval.
   If you later decide you need to edit more files, you can request those.

2. Think step-by-step and explain the needed changes in a few short sentences.

3. Describe each change with a *SEARCH/REPLACE block* per the examples below.

All changes to files must use this *SEARCH/REPLACE block* format.
ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!
{shell_cmd_prompt}
"""

    def make_main_system_prompt(self, _sitrep: ChatSitrep):
        return f"""{CoderPrompts.brade_persona_prompt}
"""

    def make_example_messages(self, sitrep: ChatSitrep):
        return [
            {
                "role": "user",
                "content": (
                    "Can you help me implement a function to calculate the factorial of a number?"
                ),
            },
            {
                "role": "assistant",
                "content": """Certainly! I'd be happy to help you implement a factorial function.
Let's start by defining the function and then we can discuss its implementation.
Here's a basic implementation in Python:

```python
def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)
```

This implementation uses recursion to calculate the factorial. Here's how it works:

1. If the input `n` is 0 or 1, the function returns 1 (as 0! and 1! are both defined as 1).
2. For any other positive integer, the function returns `n` multiplied by the factorial of `n-1`.

Would you like me to explain this implementation further, or would you prefer a different
approach, such as an iterative solution?
""",
            },
            {
                "role": "user",
                "content": (
                    "That looks good, but can we add some error handling for negative numbers?"
                ),
            },
            {
                "role": "assistant",
                "content": (
                    """Absolutely! Adding error handling for negative numbers is a great idea.
Let's modify the function to raise a `ValueError` if a negative number is provided.
Here's the updated implementation:

```python
def factorial(n):
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)
```

In this updated version:

1. We first check if the input is an integer using `isinstance(n, int)`. If not, we raise a
   `TypeError`.
2. We then check if the number is negative. If it is, we raise a `ValueError` with an appropriate
   message.
3. The rest of the function remains the same as before.

This implementation now handles negative numbers and non-integer inputs, making it more robust.
Would you like me to explain any part of this implementation in more detail?
"""
                ),
            },
        ]
