# Brade Docker Image

Brade is a fork of Aider that lets you pair program with LLMs, editing code in your local git repository.
Start a new project or work with an existing git repo.
Brade works best with Claude 3.5 Sonnet and is only tested with that model.

## Advantages of Docker Deployment

The Docker-based deployment approach offers significant advantages, especially in corporate environments:

- **Zero Dependency Issues**: Since the image is built from our tested base image, you completely avoid:
  - Corporate PyPI gaps or version inconsistencies (but make sure you are in compliance!)
  - System package installation
  - Binary compatibility problems
  - Python dependency conflicts

- **Consistent Environment**: Every deployment runs in the same container environment, eliminating "works on my machine" issues.

## Quick Start

Run brade with your current directory mounted:

```bash
docker run -it --rm -v "$PWD:/app" docker.io/deansher/brade:full
```

Optionally, specify your OpenAI API key or other environment variables directly:
```bash
docker run -it --rm -v "$PWD:/app" -e OPENAI_API_KEY=your-key-here docker.io/deansher/brade:full
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

### Command Line Arguments

Pass command line arguments directly after the image name:

```bash
docker run -it --rm -v "$PWD:/app" docker.io/deansher/brade:full --dark-mode
```

This example enables dark mode for better visibility in dark terminals. Any command line argument documented in the [Configuration Options](https://aider.chat/docs/config/options.html) can be used this way.

### Volume Mounts

The following command mounts your working directory to `/app` in the container. This is the recommended minimum for running Brade, but you can add other mount points in the same way.

```bash
docker run -it --rm -v "$PWD:/app" deansher/brade:latest
```

### User Permissions

If necessary to avoid file permission issues, run as your own user:

```bash
docker run -it --rm --user $(id -u):$(id -g) -v "$PWD:/app" deansher/brade:latest
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

The corporate build process is dependency-free because it uses our published Docker image as a base. You only need to add configuration - all runtime dependencies are already included and tested in the base image. This makes corporate deployment much simpler than direct installation, which would require managing system packages, Python dependencies, and binary compatibility.

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
