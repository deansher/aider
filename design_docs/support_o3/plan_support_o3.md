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

## Critical Constraints

1. litellm does not yet support "developer" messages
2. o3-mini no longer supports "system" messages
3. We must handle this conflict by:
   - Continuing to use "system" messages in our own code
   - Converting them to simple "user" messages at the lowest level, in sendchat.py
   - Similar to but simpler than our Anthropic message conversion
   - No need for message pairs or "Understood" responses
4. We will revisit this design after litellm adds support for "developer" messages

## Requirements

OpenAI has released a new model, o3-mini. We need to add support for this model to the Brade application. We will add support for the o3-mini model in a way that is consistent with our existing support for other models.

As our MVP, we'll use o3-mini by default for all steps of `ArchitectCoder`.

OpenAI's documentation states:

> Developer messages are the new system messages: Starting with o1-2024-12-17, reasoning models support developer messages rather than system messages, to align with the chain of command behavior described in the model spec.

Due to the Critical Constraints above, we will still support "system" messages in all of our code above a certain lowest level. At that low-level point, we will convert them as needed for the target model. We already do a conversion for Anthropic messages in `transform_messages_for_anthropic` in sendchat.py. We will add an analogous conversion for o3-mini messages.

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

- (✔︎) Add tests for o3-mini configuration
  - (✔︎) Test model settings
  - (✔︎) Test default configurations

### (✔︎) Implement Message Transformation

#### Requirements

1. Add support for converting system messages to user messages
   - Simple one-to-one conversion of each system message to a user message
   - Preserve the original order of messages
   - No special handling or message combining needed

2. Keep implementation simple and focused
   - Convert system messages to user messages at the lowest level
   - Maintain compatibility with existing code above that layer
   - No need to follow the more complex Anthropic pattern

3. Ensure proper test coverage with focused test cases
   - Test one-to-one conversion of system messages
   - Verify message order is preserved
   - No need to test message combining or special cases

#### Implementation Steps

- (✔︎) Add message transformation function
  - (✔︎) Create transform_messages_for_o3 in sendchat.py
  - (✔︎) Implement simple system-to-user conversion
  - (✔︎) Preserve message order

- (✔︎) Add focused test cases
  - (✔︎) Test basic system-to-user conversion
  - (✔︎) Test order preservation
  - (✔︎) Test mixed message types

### (✔︎) Configure Default Model Selection

#### Requirements

1. Set o3-mini as the primary default model:
   - Use for all roles in ArchitectCoder (primary, editor, reviewer)
   - Use as default for all other use cases
   - Use whenever OPENAI_API_KEY is present

2. Implement fallback logic:
   - Use latest Claude 3.5 Sonnet when only ANTHROPIC_API_KEY exists
   - Document the fallback behavior clearly in code comments

3. Ensure consistent configuration:
   - Proper edit formats for each role
   - Appropriate model settings
   - Correct prompts and message handling

#### Implementation Steps

- (✔︎) Update default model selection in main.py
  - (✔︎) Add clear comments explaining the default model strategy
  - (✔︎) Implement API key availability checks
  - (✔︎) Set o3-mini as primary default
  - (✔︎) Configure Claude 3.5 Sonnet fallback

- ( ) Verify model settings in models.py
  - ( ) Confirm o3-mini is properly configured for all roles
  - ( ) Validate edit formats for each role
  - ( ) Test model settings

- ( ) Test with different API key combinations
  - ( ) Test with both keys present
  - ( ) Test with only ANTHROPIC_API_KEY
  - ( ) Document behavior

### ( ) Validate Changes

#### Requirements

1. Ensure all tests pass
2. Verify changes work with o3-mini model
3. Confirm compatibility with existing models
4. Document any known limitations

#### Implementation Steps

- (✔︎) Run existing test suite
- ( ) Add integration tests
- ( ) Test with live o3-mini model
- ( ) Document findings and limitations
