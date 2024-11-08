from aider.coders.brade_prompts import BradePrompts
from aider.coders.editblock_coder import EditBlockCoder


class BradeCoder(EditBlockCoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edit_format = "diff"

        self.brade_prompts = BradePrompts()
        self.gpt_prompts = self.brade_prompts
