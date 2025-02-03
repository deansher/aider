# Enhance Repomap

Brade and Dean are using this document to support their collaborative process. Brade is an AI software engineer collaborating with Dean through the Brade application. We are working together to enhance the Brade application's code. This is an interesting recursive situation where Brade is helping improve her own implementation.

We want to work efficiently in an organized way. For the portions of the code that we must change to meet our functionality goals, we want to move toward beautiful, idiomatic Python code. We also want to move toward more testable code with simple unit tests that cover the most important paths.

This document contains three kinds of material:

- requirements
- specific plans for meeting those requirements
- our findings as we analyze our code along the way

For major step of the work, (each top-level bullet of each "### ( ) task" section) we will follow this process:

- Make sure our plan is current.
- Make sure we have the information we need for our next step.
  - Writing down any new findings in this document.
  - Correct anything we previously misunderstood.
- Make sure existing unit tests pass.
- Consider whether to add unit tests or do manual testing before making the code changes.
- Make the code changes.
- Run the unit tests.
- Manually validate the change.

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

OpenAI has released a new model, o3-mini. We need to add support for this model to the Brade application. We will add support for the o3-mini model in a way that is consistent with our existing support for other models.

As our MVP, we'll use o3-mini by default for all steps of `ArchitectCoder`.

OpenAI's documentation states:

> Developer messages are the new system messages: Starting with o1-2024-12-17, reasoning models support developer messages rather than system messages, to align with the chain of command behavior described in the model spec.

From some web research (February 3, 2025), this switch to "developer" messages is a challenge:
* litellm does not yet support "developer" messages.
* o3-mini no longer supports "system" messages.

We will still support "system" messages in all of our code above a certain lowest level. At that low-level point, we will convert them as needed for the target model. We already do a conversion for Anthropic messages in `transform_messages_for_anthropic` in sendchat.py. We will add an analogous conversion for o3-mini messages.

We won't change our own coding abstractions yet. Before doing that, we'll see what direction litellm's API goes with this.

## Tasks

### (✔︎) Add o3-mini Model Support

#### Requirements

1. Add o3-mini model configuration to models.py
2. Configure o3-mini as a reasoning model
3. Set appropriate defaults for the model
4. Ensure proper test coverage

#### Implementation Steps

- (✔︎) Add o3-mini model settings
  - (✔︎) Configure as reasoning model
  - (✔︎) Set appropriate edit format
  - (✔︎) Configure default models for weak/editor roles
  - (✔︎) Set other model-specific parameters

- ( ) Add tests for o3-mini configuration
  - ( ) Test model settings
  - ( ) Test reasoning model behavior
  - ( ) Test default configurations

### ( ) Implement Message Transformation

#### Requirements

1. Add support for converting system messages to developer messages
2. Handle this conversion at the lowest possible level
3. Maintain compatibility with existing code
4. Ensure proper test coverage

#### Implementation Steps

- ( ) Add message transformation function
  - ( ) Create transform_messages_for_o3 in sendchat.py
  - ( ) Follow pattern of transform_messages_for_anthropic
  - ( ) Handle system to developer message conversion

- ( ) Add tests for message transformation
  - ( ) Test basic message conversion
  - ( ) Test edge cases and error handling
  - ( ) Test integration with existing code

### ( ) Validate Changes

#### Requirements

1. Ensure all tests pass
2. Verify changes work with o3-mini model
3. Confirm compatibility with existing models
4. Document any known limitations

#### Implementation Steps

- ( ) Run existing test suite
- ( ) Add integration tests
- ( ) Test with live o3-mini model
- ( ) Document findings and limitations
