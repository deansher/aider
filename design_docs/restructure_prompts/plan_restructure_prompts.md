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

## Current Prompt Material Inventory

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

## Current Prompt Structure Analysis

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

## Planned Changes

### Testing Strategy

For each content transition:
1. Verify all existing functionality remains working:
   - Basic code editing
   - File handling
   - Git integration
   - Command processing
   
2. Test specific scenarios:
   - Multi-file edits
   - New file creation
   - Error handling
   - Complex code changes

3. Validate prompt structure:
   - XML schema compliance
   - Content placement
   - Role separation

### System Prompt Restructuring

1. Create a minimal system prompt focused on:
   - Brade's role as an expert software developer
   - Core behavioral traits (collaborative, thoughtful, professional)
   - Basic interaction parameters

2. Move to user messages:
   - Task instructions
   - Output format requirements
   - Example conversations
   - Platform information

### Document Organization

1. Implement consistent XML structure:
```xml
<context>
  <documents>
    <document>
      <path>filename.py</path>
      <content>
        [Source code]
      </content>
    </document>
  </documents>
  
  <instructions>
    [Task requirements]
  </instructions>
  
  <platform_info>
    [System details]
  </platform_info>
</context>
```

2. Place documents before instructions in all cases

3. Use clear metadata for each section

### Implementation Tasks

Phase 1: Document and Test Current State
- ( ) Create comprehensive test suite for current functionality
  - ( ) Basic code editing tests
  - ( ) File handling tests
  - ( ) Git integration tests
  - ( ) Command processing tests
- ( ) Document all current prompt components and their locations
- ( ) Map current message flow and dependencies

Phase 2: System Prompt Transition
- ( ) Create new minimal system prompt
  - ( ) Extract core role and behavioral traits
  - ( ) Remove task-specific content
  - ( ) Validate basic interaction still works
- ( ) Move task instructions to user messages
  - ( ) Create XML structure for instructions
  - ( ) Verify edit functionality preserved
  - ( ) Test error handling

Phase 3: Document Organization
- ( ) Design and implement XML schema
  - ( ) Define standard tags and structure
  - ( ) Create schema validation helpers
  - ( ) Test with sample content
- ( ) Convert existing document handling
  - ( ) Update file content formatting
  - ( ) Modify repository map structure
  - ( ) Test file operations

Phase 4: Message Flow Updates
- ( ) Implement new user message structure
  - ( ) Create XML formatters
  - ( ) Update message ordering
  - ( ) Test with complex scenarios
- ( ) Update prompt generation
  - ( ) Modify format_messages()
  - ( ) Update ChatChunks class
  - ( ) Verify all features working

Phase 5: Validation and Cleanup
- ( ) Add comprehensive validation
  - ( ) XML schema verification
  - ( ) Message structure checks
  - ( ) Content placement rules
- ( ) Final testing
  - ( ) Run full test suite
  - ( ) Performance validation
  - ( ) Error case testing

### Testing and Validation

We will validate the new structure by:
1. Verifying XML schema compliance
2. Testing prompt generation with various inputs
3. Checking alignment with guide recommendations
4. Measuring impact on model performance

## Success Criteria

The restructured prompts should:
- Follow all key recommendations in the prompting guide
- Maintain or improve model performance
- Be easy to maintain and extend
- Support future Claude model updates

