# Plan for Improving Langfuse Integration

Brade and Dean are using this document to support their collaborative process. Brade is an AI software engineer collaborating with Dean through the Brade application. We are working together to enhance the Brade application's code. This is an interesting recursive situation where Brade is helping improve her own implementation.

We want to work efficiently in an organized way. For the portions of the code that we must change to meet our functionality goals, we want to move toward beautiful, idiomatic Python code. We also want to move toward more testable code with simple unit tests that cover the most important paths.

This document is a living record of our work. It contains:

- Requirements that define what we want to achieve
- Specific plans for meeting those requirements
- Our findings as we analyze our code
- Our learnings as we complete tasks

As we work, we:

- Check off tasks as we complete them (✅)
- Document what we learn under each task
- Revise our plans based on what we learn
- Add new tasks as we discover them

For major steps of the work (each top-level bullet of each "### ( ) task" section) we follow this process:

- Make sure our plan is current.
- Make sure we have the information we need for our next step.
  - Writing down any new findings in this document.
  - Correct anything we previously misunderstood.
- Make sure existing unit tests pass.
- Consider whether to add unit tests or do manual testing before making the code changes.
- Make the code changes.
- Run the unit tests.
- Manually validate the change.
- Document what we learned.

We only intend for this plan to cover straightforward next steps to our next demonstrable milestone. We'll extend it as we go.

We write down our findings as we go, to build up context for later tasks. When a task requires analysis, we use the section header as the task and write down our findings as that section's content.

For relatively complex tasks that benefit from a prose description of our approach, we use the section header as the task and write down our approach as that section's content. We nest these sections as appropriate.

For simpler tasks that can be naturally specified in a single sentence, we move to bullet points.

We use simple, textual checkboxes at each level of task, both for tasks represented by section headers and for tasks represented by bullets. Like this:

```
### ( ) Complex Task.

- (✅) Subtask
  - (✅) Subsubtask
  - Added support for X
  - Discovered Y needs to be handled differently
- ( ) Another subtask
```

## Requirements

Rework our Langfuse integration to cleanly and thoroughly use the low-level Python SDK. In our current integration, we mostly use decorators. This has proven awkward and we want to move away from it. 

Here are some specific requirements:

- Continue capturing the useful information that we capture today.
- Cleanly capture streamed model responses as `output` of "generation" traces.
- Create a module aider/langfuse_utils.py that provides our own customized abstractions around Langfuse. (We may even define some of our own decorators here, if we see ways to use them more ergonomically.)

## Tasks

### ( ) Document the current state of our Langfuse integration.

### ( ) Document the design of our reworked integration.

### ( ) Rework one narrow piece of our integration.

Implement this using `langfuse_utils` APIs that we find we wish we had. Just scaffold them for now.

### ( ) Rework a second piece of our integration.

### ( ) Thoughtfully revise the `langfuse_utils` module API.

### ( ) Implement the `langfuse_utils` module.

### ( ) Finish migrating to our new approach.

