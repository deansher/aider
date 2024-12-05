# Brade Docker Image

Brade is a fork of Aider that lets you pair program with LLMs, editing code in your local git repository.
Start a new project or work with an existing git repo.
Brade works best with Claude 3.5 Sonnet and is only tested with that model.

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
- `brade-vX.Y.Z`: Specific version releases

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

If necessary to avoid file permission issues, run as your own user:

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
- Voice coding support
- Add images and URLs to the chat
- Uses a map of your git repo to work well in larger codebases

## Documentation

Full documentation of the upstream project available here:
- [Installation](https://aider.chat/docs/install.html)
- [Usage](https://aider.chat/docs/usage.html)
- [LLM Support](https://aider.chat/docs/llms.html)

## Support

- [GitHub Issues](https://github.com/deansher/brade/issues)
- [Contributing Guide](https://github.com/deansher/brade/blob/main/CONTRIBUTING.md)

## License

Apache License 2.0
