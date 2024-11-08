# Claude 3.5 Prompting Guide

This guide presents Anthropic's recommended practices for effectively prompting Claude models. This guide focuses on handling complex tasks and long-context scenarios. In any cases where recommendations differ by model (mostly they don’t), the main body of this document aims at 3.5 Sonnet. An appendix explains adaptations for 3.5 Haiku.

This was written by Perplexity based on Anthropic’s own recommendations.

## Core Architecture: System vs. User Messages

### System Prompt

The system prompt should be focused solely on:

- Defining Claude's role or domain expertise  
- Setting fundamental context for the interaction  
- Establishing basic behavioral parameters

Role-based prompting through the system parameter is considered the most powerful way to use system prompts, leading to enhanced accuracy, appropriate tone, and consistent responses.

### User Messages

All other elements should be placed in user messages:

- Task-specific instructions  
- Data and documents to analyze  
- Formatting requirements  
- Specific queries or requests  
- Output structure specifications

## Document Handling and Long Context

### Document Placement

Place documents near the top of your user message, above instructions and queries. This strategy can improve response quality by up to 30% for complex inputs.

### Structured Organization

Use XML tags to organize content clearly:

\<documents\>

  \<document index="1"\>

    \<source\>filename.pdf\</source\>

    \<document\_content\>

      \[Document text goes here\]

    \</document\_content\>

  \</document\>

\</documents\>

### Best Practices for Long Documents

- Break content into logical segments  
- Use consistent tagging conventions  
- Include clear metadata for each section  
- Place documents before instructions  
- Implement quote-based grounding

## Task Structure

### Instructions Component

1. Define the specific role/context  
2. Outline task requirements  
3. Specify output format

### Data Component

- Place documents and reference materials  
- Use consistent XML tagging  
- Include relevant metadata

### Query Component

- Position specific questions at the end  
- Make requests explicit and focused  
- Include output format requirements

## Advanced Techniques

### Quote-Based Grounding

For extensive documents:

1. Request relevant quotes from source material  
2. Ask for analysis based on those quotes

### Output Control

- Specify desired output format explicitly  
- Request step-by-step explanations when needed  
- Use XML tags to structure responses

## Common Pitfalls

- Mixing instructions with data  
- Placing queries before long-form content  
- Using inconsistent document structure  
- Including task instructions in system prompts  
- Omitting necessary context or metadata

## Best Practices Summary

1. Keep system prompts focused on role and context  
2. Place all documents and specific instructions in user messages  
3. Structure content with clear XML tags  
4. Position documents before instructions  
5. Make queries explicit and focused  
6. Use consistent formatting throughout

By following these guidelines, you can maximize Claude's effectiveness in handling complex tasks and processing large amounts of information. Remember that clear structure and explicit instructions are key to achieving optimal results.

## Adapting Prompts for Claude 3.5 Haiku

When adapting the main guide's prompting strategies for Haiku, focus on efficiency and conciseness while maintaining clarity:

### Prompt Structure

- Keep XML structure but with shorter document segments  
- Break complex prompts into smaller, focused interactions  
- Prioritize essential context over comprehensive background  
- Place most relevant information at the beginning of documents

### Instructions

- Write more direct, concise task descriptions  
- Focus on one primary objective per prompt  
- Reduce multi-step instructions into discrete interactions  
- Specify when brief responses are acceptable

### Document Handling

- Be more selective with included context  
- Prioritize most relevant sections of long documents  
- Consider splitting large documents across multiple interactions  
- Maintain XML structure but with shorter segments

The core prompting principles remain the same, but emphasis should be placed on efficiency and focused interactions to leverage Haiku's speed advantages.
