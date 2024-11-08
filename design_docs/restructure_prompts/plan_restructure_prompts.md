# Plan for Restructuring Brade's Prompts

Brade and Dean are using this document to support their collaborative process. Brade is an AI software engineer collaborating with Dean through the Brade application. We are working together to enhance the Brade application's code - specifically its prompt system. This is an interesting recursive situation where Brade is helping improve her own implementation.

Brade defers to Dean's leadership, but Dean also trust's Brade's judgment and wants Brade to challenge his decisions when Brade thinks that's important. 

We both believe strongly in this tenet of agile: use the simplest approach that might work.

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

### New User Message Structure

#### Semantic Markers Approach

We chose to use semantic XML-like markers rather than strict XML for several key reasons:

1. **Simplicity and Readability**
   - Markers clearly indicate content boundaries without requiring XML escaping
   - Natural content remains readable without XML entity encoding
   - Source code can be included verbatim without modification

2. **Reduced Processing Overhead** 
   - No need to escape special characters in content
   - Simpler parsing requirements
   - Lower risk of encoding/decoding errors

3. **LLM-Friendly Format**
   - Clear semantic boundaries help the LLM understand content roles
   - Natural content is easier for the LLM to process
   - Reduced token usage by avoiding XML escaping

Here's how the semantic markers structure the content:

```
<latest_context_from_system>
The Brade application puts the most recent authoritative context information here.
Content can contain <, >, & and other special characters without escaping.

<repository_map>
Repository map content appears here, including file paths like:
src/main.py -> Contains main application logic
lib/<utils>.py -> Utility functions
</repository_map>

<project_files>
Source code appears verbatim:

def hello():
    print("Hello & welcome!")
    if x < 3:
        return True
</project_files>

<platform_info>
System details appear here
</platform_info>
</latest_context_from_system>

<actions_taken_by_system>
The Brade application explains actions that it took at this point in the chat.

<action_taken>
Git commit abc123: Updated hello() function
</action_taken>
</actions_taken_by_system>
  
<instructions_from_system>
Instructions appear here
</instructions_from_system>

<message_from_user>
User message appears here
</message_from_user>
```

The markers serve as semantic boundaries while allowing content to appear naturally without escaping. This approach:

- Makes the prompts more maintainable
- Reduces complexity in the codebase
- Improves reliability by eliminating XML parsing edge cases
- Saves tokens by avoiding entity encoding
- Keeps source code readable and natural

The tradeoff is that we lose strict XML validation, but the benefits of simpler processing and natural content outweigh this limitation for our use case. The LLM is able to understand and respect the semantic boundaries without requiring strict XML compliance.

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

## Prompt Improvements to Track

### Precision About Edit Blocks
- Need to be more precise in prompts about how edit blocks are handled
- Edit blocks are automatically applied and committed by the Brade application
- I (Brade) should understand this is automated, not manual
- Important for accurate mental model of the system

### Clarity About Roles and Relationships
- Clarify that I am Brade, an AI collaborating through the Brade application
- Make clear that you are Dean, my human partner
- Acknowledge the recursive nature of improving my own implementation
- Maintain professional but friendly collaboration style

### Additional Improvements
- (Add more improvements as we discover them)

## Testing Strategy

### Unit Tests
- Add tests for XML schema validation
- Add tests for content placement rules
- Add tests for role separation

### Integration Tests
- Test basic code editing still works
- Test file handling still works
- Test git integration still works
- Test command processing still works

### Manual Testing Checklist
- Check Langfuse logs to verify prompt structure
- Basic code editing with different models
- File handling operations (add/remove/modify)
- Git operations (commit/status/diff)
- Command processing for all command types
- Error handling and recovery
- Multi-file edits
- Long conversations with history

## Implementation Strategy

### (✓) Inventory files that contain prompts.

#### Core Prompt Files
- **base_prompts.py**
  - Path: aider/coders/base_prompts.py
  - Purpose: Defines base CoderPrompts class with core prompts used by all coders
  - Contains: Main system prompts, example messages, file handling prompts
  
#### Editor-Specific Prompts
- **editblock_prompts.py**
  - Path: aider/coders/editblock_prompts.py
  - Purpose: Prompts for edit block style code modifications
  - Contains: Search/replace block format rules and examples

- **editblock_fenced_prompts.py**
  - Path: aider/coders/editblock_fenced_prompts.py
  - Purpose: Variation of edit block prompts using fenced code blocks
  - Contains: Example messages with fenced formatting

- **editor_editblock_prompts.py**
  - Path: aider/coders/editor_editblock_prompts.py
  - Purpose: Specialized prompts for editor mode using edit blocks
  - Contains: Simplified system prompts without shell commands

#### Whole File Prompts
- **wholefile_prompts.py**
  - Path: aider/coders/wholefile_prompts.py
  - Purpose: Prompts for whole file editing mode
  - Contains: File listing format rules and examples

- **editor_whole_prompts.py**
  - Path: aider/coders/editor_whole_prompts.py
  - Purpose: Editor mode prompts for whole file editing
  - Contains: Simplified system prompts for whole file edits

#### Function-Based Prompts
- **wholefile_func_prompts.py**
  - Path: aider/coders/wholefile_func_prompts.py
  - Purpose: Function-based prompts for whole file editing
  - Contains: write_file function definition and usage

- **single_wholefile_func_prompts.py**
  - Path: aider/coders/single_wholefile_func_prompts.py
  - Purpose: Single file version of function-based prompts
  - Contains: Simplified write_file function prompts

#### Special Purpose Prompts
- **architect_prompts.py**
  - Path: aider/coders/architect_prompts.py
  - Purpose: Prompts for architect mode planning and analysis
  - Contains: Two-step planning and implementation process

- **ask_prompts.py**
  - Path: aider/coders/ask_prompts.py
  - Purpose: Prompts for question answering mode
  - Contains: Code analysis and explanation prompts

- **help_prompts.py**
  - Path: aider/coders/help_prompts.py
  - Purpose: Prompts for help and documentation mode
  - Contains: Aider usage and documentation assistance

- **brade_prompts.py**
  - Path: aider/coders/brade_prompts.py
  - Purpose: Specialized prompts for Brade persona
  - Contains: Enhanced collaboration and personality traits

#### Unified Diff Prompts
- **udiff_prompts.py**
  - Path: aider/coders/udiff_prompts.py
  - Purpose: Prompts for unified diff style editing
  - Contains: Diff format rules and examples

### ( ) Further Prep for Prompt Restructuring
- (✓) Create backup copies of all prompt files before making changes
- (✓) Analyze common patterns and shared content across prompt files

#### Common Patterns Analysis

##### Message Types
1. System Messages
   - Role/identity definition (all coders)
   - Core behavioral traits
   - Basic context setting
   
2. File Content Messages
   - Source code display
   - Read-only reference content
   - Repository mapping
   - Common format: filename + fence + content

3. Instruction Messages
   - Task-specific commands
   - Format requirements
   - Response guidelines
   - Platform-specific details

4. Status/Action Messages
   - Git commit notifications
   - File additions/changes
   - Command results
   - Error reports

##### Shared Content Areas
1. Core Prompts (base_prompts.py)
   - System message foundation
   - File handling templates
   - Basic instructions
   - Used by all other prompt files

2. Edit Format Instructions
   - Search/replace blocks
   - Whole file updates
   - Unified diffs
   - Function calls
   - Each has similar structure but different syntax

3. Example Messages
   - Most prompt files include examples
   - Similar structure but different content
   - Could be standardized and shared

4. Shell Command Handling
   - Present in multiple prompt files
   - Consistent structure
   - Platform-specific variations

##### Consolidation Opportunities
1. Merge Common System Content
   - Combine core role/identity content
   - Share basic behavioral traits
   - Standardize context setting

2. Standardize File Handling
   - Create shared file display format
   - Unify read-only file handling
   - Standardize repository mapping

3. Unify Instruction Format
   - Create consistent XML structure
   - Share common instructions
   - Allow coder-specific extensions

4. Centralize Examples
   - Create shared example library
   - Allow coder-specific examples
   - Maintain consistent format

##### Semantic Marker Structure
1. Core Message Markers
   ```
   <system_context>
   <file_content>
   <instructions>
   <status_update>
   ```

2. Content Organization Markers
   ```
   <edit_format>
   <examples>
   <shell_commands>
   ```

3. Extension Markers
   ```
   <coder_specific>
   <custom_instructions>
   ```

- ( ) Identify opportunities for consolidation and standardization
- ( ) Plan XML schema to accommodate all prompt types

### ( ) Document Message Structure Guidelines
- ( ) Define standard semantic markers and their usage
- ( ) Document best practices for marker placement and content formatting
- ( ) Create helper methods for consistent marker handling
- ( ) Add validation to ensure proper marker structure
- ( ) Add unit tests for marker validation

### ( ) Decide whether to make any repo map formatting changes

### ( ) Implement New Structure

- ( ) Add semantic markers for repository map
  ```
  <repository_map>
  [Repository map content]
  </repository_map>
  ```

- ( ) Add semantic markers for file content
  ```
  <project_files>
  [File content]
  </project_files>
  ```

- ( ) Add semantic markers for system actions
  ```
  <actions_taken_by_system>
  <action_taken>[Description]</action_taken>
  </actions_taken_by_system>
  ```

- ( ) Add semantic markers for user messages
  ```
  <message_from_user>[User message]</message_from_user>
  ```

- ( ) Add semantic markers for system instructions
  ```
  <instructions_from_system>[Instructions]</instructions_from_system>
  ```

- ( ) Update tests for each marker structure

- ( ) Verify all functionality works with new structure

### ( ) Move Content (one atomic step per item)
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

### ( ) Cleanup and Documentation
- ( ) Remove redundant content
- ( ) Update documentation
- ( ) Final testing pass
- ( ) Document any remaining issues

