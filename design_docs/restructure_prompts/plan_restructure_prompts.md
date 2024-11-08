# Plan for Restructuring Prompts

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
- Improve clarity of prompt contents.
- Improve the overall flow of prompts and content across the chat message sequence, to make it
  easier for the model to understand what is going on.

## Current State Analysis

### Key Findings
- Our system prompts contain much material that should be in user messages
- We lack consistent structure for document content
- Our `<SYSTEM>` markers don't align with XML best practices
- We mix instructions with content in ways that make the chat history harder to follow
- Our current approach makes it hard to validate prompt structure

### Current Pain Points
- Hard to verify prompt structure is correct
- Duplicate content between system and user messages
- Inconsistent formatting makes maintenance harder
- Chat history becomes confusing when instructions mix with content

## Inventory of Current Prompt Material

### System Messages in base_prompts.py

#### Core Role and Persona (brade_persona_prompt)
- Expert software engineer identity
- Collaboration style and approach
- Core beliefs about software development
- Understanding of relative strengths/weaknesses

#### Task Instructions (main_system)
- Code editing requirements
- File handling rules
- Response format specifications
- Example conversations
- Platform-specific details

### User Message Components

#### Document Content Messages
- Source code files content
- Read-only reference files
- Repository map information
- File status notifications

#### Control Messages
- File addition notifications
- Git commit notifications
- Command processing results

### Current Message Flow
- System message sets role and task framework
- Repository and file content provided
- User query or request
- Assistant response with edits

## Analysis of Current Approach

### System Messages Issues

Our current system prompts contain:
- Role definition and persona characteristics
- Task instructions and requirements
- Output format specifications
- Example conversations
- Platform-specific information

This violates the guide's recommendation that system prompts should focus solely on:
- Defining Claude's role/expertise
- Setting fundamental context
- Establishing basic behavioral parameters

### Document Handling Issues

Currently we:
- Mix instructions with document content
- Use inconsistent document organization
- Place documents after instructions in some cases
- Use `<SYSTEM>` markers that don't align with XML structure

### Task Structure Issues

Our current approach:
- Combines role definition with task instructions in system messages
- Lacks clear separation between instructions and data
- Uses markdown-style formatting instead of XML
- Places queries before supporting content

## Testing Strategy

### Unit Tests
- ( ) Add tests for XML schema validation
- ( ) Add tests for content placement rules
- ( ) Add tests for role separation

### Integration Tests
- ( ) Test basic code editing still works
- ( ) Test file handling still works
- ( ) Test git integration still works
- ( ) Test command processing still works

### Manual Testing Checklist
- ( ) Basic code editing with different models
- ( ) File handling operations (add/remove/modify)
- ( ) Git operations (commit/status/diff)
- ( ) Command processing for all command types
- ( ) Error handling and recovery
- ( ) Multi-file edits
- ( ) Long conversations with history

## Validation Steps

After each atomic change:
1. Run unit tests
2. Run integration tests
3. Check Langfuse logs to verify prompt structure
4. Run manual test checklist
5. Document any issues found

## Implementation Strategy

### ( ) Phase 1: Preparation
- ( ) Create XML schema for all message types
  - Define standard tags and structure
  - Document best practices and reasoning
  - Create schema validation helpers
  - Add unit tests
- ( ) Make backup copies of all prompt files
- ( ) List all files containing prompts
  - Organize by logical categories
  - Document file paths and purposes
- ( ) Decide on repo map formatting changes

### ( ) Phase 2: Move Content (one atomic step per item)
- ( ) Move platform info from system to user messages
  - Remove from: base_prompts.py system message
  - Add to: final user message XML structure
  - Update tests
  - Verify functionality
- ( ) Move task instructions from system to user messages
  - Remove from: system prompt
  - Add to: user message instructions section
  - Update tests
  - Verify functionality
- ( ) Move example conversations to user messages
  - Remove from: system prompt
  - Add to: appropriate user message sections
  - Update tests
  - Verify functionality

### ( ) Phase 3: Implement New Structure
- ( ) Add XML wrapper for repository map
  ```xml
  <repository_map>
    [Repository map content with consistent structure]
  </repository_map>
  ```
- ( ) Add XML wrapper for file content
  ```xml
  <project_files>
    <project_file>
      <path>filename.py</path>
      <content>[File content]</content>
    </project_file>
  </project_files>
  ```
- ( ) Add XML wrapper for system actions
  ```xml
  <actions_taken_by_system>
    <action_taken>[Description]</action_taken>
  </actions_taken_by_system>
  ```
- ( ) Add XML wrapper for user messages
  ```xml
  <message_from_user>[User message]</message_from_user>
  ```
- ( ) Add XML wrapper for system instructions
  ```xml
  <instructions_from_system>[Instructions]</instructions_from_system>
  ```
- ( ) Update tests for each wrapper
- ( ) Verify all functionality works with new structure

### ( ) Phase 4: Cleanup and Documentation
- ( ) Remove redundant content
- ( ) Update documentation
- ( ) Final testing pass
- ( ) Document any remaining issues

