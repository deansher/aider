from aider.coders.chat_chunks import ChatChunks
from aider.coders.editblock_coder import EditBlockCoder
from aider.coders.brade_prompts import BradePrompts
from aider.coders.chat_sitrep import ChatSitrep


class BradeCoder(EditBlockCoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edit_format = "diff"

        self.brade_prompts = BradePrompts()

        # We construct a new `gpt_prompts` at every chat turn.
        self.gpt_prompts = None
