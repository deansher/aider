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
- `full`: Full image with all features
- `core`: Minimal image with core functionality

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

## Corporate Deployment

Organizations can build custom Docker images that enforce specific settings while still allowing user customization.

### Building a Corporate Image

1. Copy the templates:
   ```bash
   mkdir -p corporate-brade
   cp docker/corporate/Dockerfile.template corporate-brade/Dockerfile
   cp docker/corporate/corporate-config.yml.template corporate-brade/corporate-config.yml
   cp docker/corporate/build.py corporate-brade/build.py
   chmod +x corporate-brade/build.py
   ```

2. Edit `corporate-config.yml`:
   - Set required API endpoints
   - Configure model selection
   - Set security policies
   - Add other enforced settings
   
   The configuration file uses the same format as `.aider.conf.yml`. See [Configuration Options](https://aider.chat/docs/config/options.html) for all available settings.

3. Build the corporate image:
   ```bash
   cd corporate-brade
   ./build.py --config corporate-config.yml --tag your-registry/brade:corporate
   ```

### Configuration Hierarchy

1. Command-line arguments from corporate Dockerfile (highest priority, enforced)
2. User's .aider.conf.yml in current directory
3. User's .aider.conf.yml in git root
4. User's .aider.conf.yml in home directory
5. User's .env file (similar precedence)
6. Environment variables

### Security Considerations

- Store API keys and secrets in your corporate secrets management system
- Use your corporate container registry
- Consider network isolation requirements
- Review and enforce security-related settings

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
- [Configuration Options](https://aider.chat/docs/config/options.html)

## Support

- [GitHub Issues](https://github.com/deansher/brade/issues)
- [Contributing Guide](https://github.com/deansher/brade/blob/main/CONTRIBUTING.md)

## License

Apache License 2.0
