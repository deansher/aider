# Plan for Incorporating diff-match-patch Into editblock_coder.py

We are collaborating to enhance our Python project as described below. We want to work efficiently in an organized way. For the portions of the code that we must change to meet our functionality goals, we want to move toward beautiful, idiomatic Python code with modern type hints.

This document contain three kinds of material:
- requirements
- specific plans for meeting those requirements
- our findings as we analyze our code along the way

We write down our findings as we go, to build up context for later tasks. When a task requires analysis, we use the section header as the task and write down our findings as that section's content.

For relatively complex tasks that benefit from a prose description of our approach, we use the section header as the task and write down our approach as that section's content. We nest these sections as appropriate.

For simpler tasks that can be naturally specified in a single sentence, we move to bullet points.

We use simple, textual checkboxes at each level of task, both for tasks represented by section headers and for tasks represented by bullets. Like this:

```
### ( ) Complex Task

- (✔︎) Subtask
  - (✔︎) Subsubtask
- ( ) Another subtask
```

## Requirements

Change editblock_coder.py to more reliably apply search/replace blocks by using the diff-match-patch library for soft matches between the search block and the target content. Choose tolerances to accurately handle three situations:

- If the differences between search block and target content are just minor LLM inaccuracies, such as extra spaces or line breaks, small missing comments, or slight punctuation differences, then the search block should still match the target content.

- If the differences are large enough to suggest that the LLM doesn't accurately see the target content, then this should not match.

- In an intermediate case, if the search block doesn't uniquely match one region of the target file, or if it is unclear whether the LLM clearly saw its intended match target, then this should not match.

Simplify the code by removing homegrown heuristics.

Correspondingly update tests.

When the match fails, provide clearer feedback to the LLM (i.e. to the editor assistant).

When the match fails and we retry ("reflection"), retain the entire dialog (all messages) between the editor assistant and the business logic in the chat history so that `ArchitectCoder`'s review pass fully understands what happened.

## Tasks

### ( ) Integrate diff‐match‐patch into editblock_coder.py

- ( ) Replace the existing homegrown fuzzy matching in replace_most_similar_chunk with diff‐match‐patch based matching.
- ( ) Configure matching tolerances so that:
  - Minor differences (extra spaces, inconsistent line breaks, slight punctuation variations) are tolerated.
  - Significant mismatches are rejected.
  - Ambiguous or non-unique matches are flagged as failures.
- ( ) Update error handling to provide clear feedback when no match is found.

### ( ) Update and Expand Unit Tests

- ( ) Revise tests in tests/basic/test_editblock.py to reflect the new matching behavior.
- ( ) Add tests for:
  - Tolerance of minor inaccuracies.
  - Rejection of significant mismatches.
  - Detection of ambiguous matches.
- ( ) Confirm that error messages clearly identify match failures.

### ( ) Enhance Feedback and Dialog Logging

- ( ) Retain full dialog history during reflection so that ArchitectCoder’s review sees complete context.
- ( ) Update logs to indicate how diff‐match‐patch interpreted the search/replace block.

### ( ) Code Cleanup and Documentation

- ( ) Remove obsolete heuristics and matching hacks.
- ( ) Add inline documentation in editblock_coder.py on diff‐match‐patch integration and tolerance settings.
- ( ) Update overall project documentation to describe the new matching mechanism.

## Tasks
