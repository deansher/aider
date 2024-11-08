# Plan for Improving `ArchitectCoder`

You and I often collaborate on projects. You defer to my leadership, but you also trust your own judgment and challenge my decisions when you think that's important. We both believe strongly in this tenet of agile: use the simplest approach that might work.

We are collaborating to enhance our Python project as described below. We want to work efficiently in an organized way. For the portions of the code that we must change to meet our functionality goals, we want to move toward beautiful, idiomatic Python code. We also want to move toward more testable code with simple unit tests that cover the most important paths.

This document contains three kinds of material:

- requirements
- specific plans for meeting those requirements
- our findings as we analyze our code along the way

We only intend for this plan to cover straightforward next steps to our next demonstrable milestone. We'll extend it as we go.

We write down our findings as we go, to build up context for later tasks. When a task requires analysis, we use the section header as the task and write down our findings as that section's content.

For relatively complex tasks that benefit from a prose description of our approach, we use the section header as the task and write down our approach as that section's content. We nest these sections as appropriate.

For simpler tasks that can be naturally specified in a single sentence, we move to bullet points.

We use simple, textual checkboxes at each level of task, both for tasks represented by section headers and for tasks represented by bullets. Like this:

```
### ( ) Complex Task.

- (✔︎) Subtask
  - (✔︎) Subsubtask
- ( ) Another subtask
```

## Requirements

- Restructure our prompts to optimize for Claude 3.5 Sonnet v2.
- Follow the guidelines in [Claude 3.5 Prompting Guide](../anthropic_docs/claude_prompting_guide.md).
- Structure our final user message for each completion call as follows:
  - An opening sentence that tells the model to expect supporting material followed by the user's message.
  - Supporting material organized as simple XML.
  - The user's message.
- Drop the `<SYSTEM>` markers we currently use.

