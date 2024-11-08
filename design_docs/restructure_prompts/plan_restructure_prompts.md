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

For each stage of the change:

1. Review how the code ensures proper code structure.
   - XML schema compliance
   - Content placement
   - Role separation

2. Review unit tests to see if any should be added, deleted, or changed.

3. Inspect actual prompts in Langfuse to verify structure.

4. Manually verify that existing functionality remains working:
   - Basic code editing
   - File handling
   - Git integration
   - Command processing
   
## Planned Changes

### User Message Structure

1. Implement consistent XML structure in each user message:
```xml
<latest_context_from_system>
  [The Brade application puts the most recent authoritative context information here, structured as shown below.]
  <repository_map>
    [Repository map]
  </repository_map>
  <project_files>
    <project_file>
      <path>filename.py</path>
      <content>
        [File content]
      </content>
    </project_file>
  </project_files>
  <platform_info>
    [System details]
  </platform_info>
</latest_context_from_system>

<actions_taken_by_system>
  [The Brade application explains actions that it took at this point in the chat.]
  <action_taken>
    [Description of Brade application action.]
  </action_taken>
</actions_taken_by_system>
  
<instructions_from_system>
    [instructions]
</instructions_from_system>

<message_from_user>
  [User message]
</message_from_user>

### System Versus User Prompt Restructuring

1. Create a minimal system prompt, structured as XML and covering the following:
   - Brade's role and expertise.
   - Introduce the Brade application, as distinct from Brade as a persona. 
   - Explain the Brade application's role.
   - Brade's behavioral traits (collaborative, thoughtful, professional)
   - Brade's interaction parameters
   - Reproduce the documentation of the user message XML structure provided above.

2. Place in each user message, where it will stay in the chat history:
   <instructions_from_system>...<instructions_from_system>

3. Place temporarily in the final user message before chat completion, but do not keep it in the chat history:
   <latest_context_from_system>...</latest_context_from_system>
```

2. Add the above documentation of user message structure to the system prompt.

3. Place documents before instructions in all cases

4. Use clear metadata for each section

## ( ) Test current state.

- ( ) Fix broken existing tests.
- ( ) Consider whether to add tests to get better coverage in areas we will change.

## ( ) List all files that contain prompts.

Add that information to this section.
Organize this as a hiearchical list, with the top level being logical categories, and each leaf being a file.

## ( ) Make copies of all files that contain prompts, with extensions like `.py_old`.

## ( ) Decide whether we will change the formatting of the Repo Map.

## ( ) Design and implement XML schema

- ( ) Document the best practices we will follow and our reasoning in choosing those.
- ( ) Define standard tags and structure
- ( ) Create schema validation helpers
- ( ) Create XML formatters
- ( ) Add unit tests.

## ( ) Restructure portion of the final user message that is standardized across all `Coder` subclasses.

- ( ) Implement XML structure for the material we automatically insert in it.
- ( ) Implement XML structure for the message itself.
  - ( ) Add material from the existing system prompt where appropriate, even though
        for now it will be redundant.
- ( ) Add unit tests.

## ( ) Restructure the system prompt.

- ( ) Restructure as XML, while dropping material we placed in the final user message instead.
- ( ) Add unit tests.

## ( ) Restructure and reword user messages that report actions taken by the Brade application.

