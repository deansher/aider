from .ask_prompts import AskPrompts
from .base_coder import Coder


class AskCoder(Coder):
    """Ask questions about code without making any changes."""

    edit_format = "ask"
    produces_code_edits = False  # Ask coder doesn't produce code edits
    gpt_prompts = AskPrompts()
