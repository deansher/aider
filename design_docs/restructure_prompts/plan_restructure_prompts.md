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

## Current Prompt Structure Analysis

### System Messages

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

### Document Handling

Currently we:
- Mix instructions with document content
- Use inconsistent document organization
- Place documents after instructions in some cases
- Use `<SYSTEM>` markers that don't align with XML structure

### Task Structure 

Our current approach:
- Combines role definition with task instructions in system messages
- Lacks clear separation between instructions and data
- Uses markdown-style formatting instead of XML
- Places queries before supporting content

## Planned Changes

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

- ( ) Create new minimal system prompt
  - Focus solely on role and core traits
  - Remove all task-specific content
  
- ( ) Design XML schema for document organization
  - Define standard tags and structure
  - Create validation helpers
  
- ( ) Implement new user message structure
  - Move content from system prompt
  - Organize using XML schema
  - Place documents first
  
- ( ) Update prompt generation code
  - Modify format_messages() 
  - Update ChatChunks class
  - Add XML formatting helpers

- ( ) Add validation and testing
  - Verify XML structure
  - Test prompt generation
  - Validate against guide requirements

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

