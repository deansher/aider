[docs.anthropic.com /en/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)

# Prompt Caching (beta) - Anthropic

7-9 minutes

---

Prompt Caching is a powerful feature that optimizes your API usage by allowing resuming from specific prefixes in your prompts. This approach significantly reduces processing time and costs for repetitive tasks or prompts with consistent elements.

Here’s an example of how to implement Prompt Caching with the Messages API using a `cache_control` block:

In this example, the entire text of “Pride and Prejudice” is cached using the `cache_control` parameter. This enables reuse of this large text across multiple API calls without reprocessing it each time. Changing only the user message allows you to ask various questions about the book while utilizing the cached content, leading to faster responses and improved efficiency.

---

## How Prompt Caching works

When you send a request with Prompt Caching enabled:

1. The system checks if the prompt prefix is already cached from a recent query.
2. If found, it uses the cached version, reducing processing time and costs.
3. Otherwise, it processes the full prompt and caches the prefix for future use.

This is especially useful for:

- Prompts with many examples
- Large amounts of context or background information
- Repetitive tasks with consistent instructions
- Long multi-turn conversations

The cache has a 5-minute lifetime, refreshed each time the cached content is used.

---

## Pricing

Prompt Caching introduces a new pricing structure. The table below shows the price per token for each supported model:

|Model|Base Input Tokens|Cache Writes|Cache Hits|Output Tokens|
|---|---|---|---|---|
|Claude 3.5 Sonnet|$3 / MTok|$3.75 / MTok|$0.30 / MTok|$15 / MTok|
|Claude 3 Haiku|$0.25 / MTok|$0.30 / MTok|$0.03 / MTok|$1.25 / MTok|
|Claude 3 Opus|$15 / MTok|$18.75 / MTok|$1.50 / MTok|$75 / MTok|

Note:

- Cache write tokens are 25% more expensive than base input tokens
- Cache read tokens are 90% cheaper than base input tokens
- Regular input and output tokens are priced at standard rates

---

## How to implement Prompt Caching

### Supported models

Prompt Caching is currently supported on:

- Claude 3.5 Sonnet
- Claude 3 Haiku
- Claude 3 Opus

### Structuring your prompt

Place static content (tool definitions, system instructions, context, examples) at the beginning of your prompt. Mark the end of the reusable content for caching using the `cache_control` parameter.

Cache prefixes are created in the following order: `tools`, `system`, then `messages`.

Using the `cache_control` parameter, you can define up to 4 cache breakpoints, allowing you to cache different reusable sections separately.

### Cache Limitations

The minimum cacheable prompt length is:

- 1024 tokens for Claude 3.5 Sonnet and Claude 3 Opus
- 2048 tokens for Claude 3 Haiku

Shorter prompts cannot be cached, even if marked with `cache_control`. Any requests to cache fewer than this number of tokens will be processed without caching. To see if a prompt was cached, see the response usage [fields](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching#tracking-cache-performance).

The cache has a 5 minute time to live (TTL). Currently, “ephemeral” is the only supported cache type, which corresponds to this 5-minute lifetime.

### What can be cached

Every block in the request can be designated for caching with `cache_control`. This includes:

- Tools: Tool definitions in the `tools` array
- System messages: Content blocks in the `system` array
- Messages: Content blocks in the `messages.content` array, for both user and assistant turns
- Images: Content blocks in the `messages.content` array, in user turns
- Tool use and tool results: Content blocks in the `messages.content` array, in both user and assistant turns

Each of these elements can be marked with `cache_control` to enable caching for that portion of the request.

### Tracking cache performance

Monitor cache performance using these API response fields, within `usage` in the response (or `message_start` event if [streaming](https://docs.anthropic.com/en/api/messages-streaming)):

- `cache_creation_input_tokens`: Number of tokens written to the cache when creating a new entry.
- `cache_read_input_tokens`: Number of tokens retrieved from the cache for this request.

### Best practices for effective caching

To optimize Prompt Caching performance:

- Cache stable, reusable content like system instructions, background information, large contexts, or frequent tool definitions.
- Place cached content at the prompt’s beginning for best performance.
- Use cache breakpoints strategically to separate different cacheable prefix sections.
- Regularly analyze cache hit rates and adjust your strategy as needed.

### Optimizing for different use cases

Tailor your Prompt Caching strategy to your scenario:

- Conversational agents: Reduce cost and latency for extended conversations, especially those with long instructions or uploaded documents.
- Coding assistants: Improve autocomplete and codebase Q&A by keeping relevant sections or a summarized version of the codebase in the prompt.
- Large document processing: Incorporate complete long-form material including images in your prompt without increasing response latency.
- Detailed instruction sets: Share extensive lists of instructions, procedures, and examples to fine-tune Claude’s responses. Developers often include an example or two in the prompt, but with prompt caching you can get even better performance by including 20+ diverse examples of high quality answers.
- Agentic tool use: Enhance performance for scenarios involving multiple tool calls and iterative code changes, where each step typically requires a new API call.
- Talk to books, papers, documentation, podcast transcripts, and other longform content: Bring any knowledge base alive by embedding the entire document(s) into the prompt, and letting users ask it questions.

### Troubleshooting common issues

If experiencing unexpected behavior:

- Ensure cached sections are identical and marked with cache_control in the same locations across calls
- Check that calls are made within the 5-minute cache lifetime
- Verify that `tool_choice` and image usage remain consistent between calls
- Validate that you are caching at least the minimum number of tokens

Note that changes to `tool_choice` or the presence/absence of images anywhere in the prompt will invalidate the cache, requiring a new cache entry to be created.

---

## Cache Storage and Sharing

- **Organization Isolation**: Caches are isolated between organizations. Different organizations never share caches, even if they use identical prompts..
    
- **Exact Matching**: Cache hits require 100% identical prompt segments, including all text and images up to and including the block marked with cache control. The same block must be marked with cache_control during cache reads and creation.
    
- **Output Token Generation**: Prompt caching has no effect on output token generation. The response you receive will be identical to what you would get if prompt caching was not used.
    

---

## Prompt Caching examples

To help you get started with Prompt Caching, we’ve prepared a [prompt caching cookbook](https://github.com/anthropics/anthropic-cookbook/blob/main/misc/prompt_caching.ipynb) with detailed examples and best practices.

Below, we’ve included several code snippets that showcase various Prompt Caching patterns. These examples demonstrate how to implement caching in different scenarios, helping you understand the practical applications of this feature:

---

## FAQ