# Brade Docker Image

Brade is a fork of Aider that lets you pair program with LLMs, editing code in your local git repository.
Start a new project or work with an existing git repo.
Brade works best with GPT-4o & Claude 3.5 Sonnet and can connect to almost any LLM.

## Quick Start

```bash
# Run brade with your current directory mounted
docker run -it --rm \
  -v "$PWD:/app" \
  deansher/brade:latest

# Or specify your OpenAI API key directly
docker run -it --rm \
  -v "$PWD:/app" \
  -e OPENAI_API_KEY=your-key-here \
  deansher/brade:latest
```

## Available Tags

- `latest`: Latest stable release
- `vX.Y.Z`: Specific version releases
- `full`: Includes all optional dependencies
- `core`: Minimal image with core functionality only

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- Other API keys as documented at [aider.chat/docs/llms.html](https://aider.chat/docs/llms.html)

### Volume Mounts

Mount your working directory to `/app` in the container:

```bash
docker run -it --rm \
  -v "$PWD:/app" \
  deansher/brade:latest
```

### User Permissions

To avoid file permission issues, run as your user:

```bash
docker run -it --rm \
  --user $(id -u):$(id -g) \
  -v "$PWD:/app" \
  deansher/brade:latest
```

## Features

- Edit multiple files at once
- Automatic git commits with sensible messages
- Works with most popular languages
- Connects to GPT-4o, Claude 3.5 Sonnet, and many other LLMs
- Voice coding support
- Add images and URLs to the chat
- Uses a map of your git repo to work well in larger codebases

## Documentation

Full documentation available at:
- [Installation](https://aider.chat/docs/install.html)
- [Usage](https://aider.chat/docs/usage.html)
- [LLM Support](https://aider.chat/docs/llms.html)

## Support

- [GitHub Issues](https://github.com/deansher/brade/issues)
- [Contributing Guide](https://github.com/deansher/brade/blob/main/CONTRIBUTING.md)

## License

Apache License 2.0
