
# Contributing to the Project

Please consider submitting your PRs to the [Aider](https://github.com/paul-gauthier/aider)
project instead of this one, because our goal is to stay as close to that project as possible.
But if you want to propose a change to Brade-specific functionality in a way that still 
minimizes divergence from the main project, then sure, we'll take a look.

I'm saying "we" here in case someone joins the "we" one day. It could be you! But meanwhile, I just mean me, Dean.

## Bug Reports and Feature Requests

Please submit bug reports and feature requests as GitHub issues. This
helps us to keep track of them and discuss potential solutions or
enhancements.

## Pull Requests

We appreciate your pull requests. For small changes, feel free to
submit a PR directly. If you are considering a large or significant
change, please discuss it in a GitHub issue before submitting the
PR. This will save both you and the maintainers time, and it helps to
ensure that your contributions can be integrated smoothly.

## Licensing

Before contributing a PR, please review our
[Individual Contributor License Agreement](https://aider.chat/docs/legal/contributor-agreement.html).
All contributors will be asked to complete the agreement as part of the PR process.

## Setting up a Development Environment

### Clone the Repository

```
git clone https://github.com/deansher/brade.git
cd brade
```

### Create a Virtual Environment

It is recommended to create a virtual environment outside of the repository to keep your development environment isolated.

#### Using `venv` (Python 3.9 and later)

```
python -m venv /path/to/venv
```

#### Using `virtualenv` (for older Python versions)

```
pip install virtualenv
virtualenv /path/to/venv
```

### Activate the Virtual Environment

#### On Windows

```
/path/to/venv/Scripts/activate
```

#### On Unix or macOS

```
source /path/to/venv/bin/activate
```

### Install the Project in Editable Mode

This step allows you to make changes to the source code and have them take effect immediately without reinstalling the package.

```
pip install -e .
```

### Install the Project Dependencies

```
pip install -r requirements.txt
```

For development, at least install the development dependencies:

```
pip install -r requirements/requirements-dev.txt
```

Consider installing other optional dependencies from the `requirements/` directory, if your development work needs them. 

Note that these dependency files are generated by `./scripts/pip-compile.sh` and then committed. See [Managing Dependencies](#managing-dependencies).

### Install Pre-commit Hooks (Optional)

The project uses pre-commit hooks for code formatting and linting. If you want to install and use these hooks, run:

```
pre-commit install
```

This will automatically run the pre-commit hooks when you commit changes to the repository.

Now you should have a fully functional development environment for the Brade project. You can start making changes, running tests, and contributing to the project.

### Handy Opinionated Setup Commands for MacOS / Linux

Here's an example of following the setup instructions above, for your copy/paste pleasure if your system works the same. Start in the project directory.

```
python3 -m venv --clear ../brade_venv \
 && source ../brade_venv/bin/activate \
 && python -m pip install --upgrade pip \
 && pip install -e . \
 && pip install -r requirements.txt \
 && pip install -r requirements/requirements-dev.txt
```

### Running Tests

Just run `pytest`.

### Building and Testing the Docker Image

The project includes Docker support for both individual and corporate use:

#### Standard Docker Images

There are two standard build targets:

- `brade-full`: Includes all dependencies including help documentation
- `brade-core`: Minimal image with core functionality only

Note: Due to Docker security requirements, you should use fully qualified image names that include the registry prefix (`docker.io`) and repository owner (`deansher`). This ensures consistent behavior across different Docker configurations and environments.

To build either target:

```bash
# Build the full image. This is what we ship as deansher/brade.
docker build -t docker.io/deansher/brade:full --target brade-full -f docker/Dockerfile .

# Build the core image 
docker build -t docker.io/deansher/brade:core --target brade-core -f docker/Dockerfile .
```

#### Corporate Docker Builds

For corporate deployments, we provide tooling to build customized images that enforce corporate policies while still allowing user customization. The corporate build process uses our published images as a base.

##### Setup Corporate Build

1. Copy the templates:
   ```bash
   mkdir -p corporate-brade
   cp docker/corporate/Dockerfile.template corporate-brade/Dockerfile
   cp docker/corporate/corporate-config.yml.template corporate-brade/corporate-config.yml
   cp docker/corporate/build.py corporate-brade/build.py
   chmod +x corporate-brade/build.py
   ```

2. Edit `corporate-config.yml` to set your corporate policies:
   - Set required API endpoints
   - Configure model selection
   - Set security policies
   - Add other enforced settings

3. Build the corporate image:
   ```bash
   cd corporate-brade
   ./build.py --config corporate-config.yml --tag your-registry/brade:corporate
   ```

The build script will:
- Validate your configuration
- Generate appropriate command-line arguments
- Build a Docker image that enforces corporate settings
- Allow users to still customize non-enforced settings

#### Testing Docker Images

To test any Docker image locally, you'll need to:
1. Build the image (as shown above)
2. Run a container with appropriate permissions and volume mounts

Here's a recommended run command. If the docker image can't then read and write to your current working directory, 
leave out the `--user ...` line.

```bash
docker run --rm -it \
  --user $(id -u):$(id -g) \
  -v "$PWD:/app" \
  your-image-name
```

Key options explained:
- `--user $(id -u):$(id -g)`: Runs brade within container as your user and group
- `-v "$PWD:/app"`: Mounts current directory into container for accessing local files
- `--rm`: Automatically removes container when it exits
- `-it`: Provides interactive terminal for input/output

For the standard images, use:
- Full image: `docker.io/deansher/brade:full`
- Core image: `docker.io/deansher/brade:core`

For corporate images, use your corporate registry and tag.

### Building the Documentation

The project's documentation is built using Jekyll and hosted on GitHub Pages. To build the documentation locally, follow these steps:

1. Install Ruby and Bundler (if not already installed).
2. Navigate to the `aider/website` directory.
3. Install the required gems:
   ```
   bundle install
   ```
4. Build the documentation:
   ```
   bundle exec jekyll build
   ```
5. Preview the website while editing (optional):
   ```
   bundle exec jekyll serve
   ```

The built documentation will be available in the `aider/website/_site` directory.

## Coding Standards

### Python Compatibility

Brade supports Python versions 3.10, 3.11, 3.12, and 3.13. When contributing code, ensure compatibility with these supported Python versions.

### Code Style

We are gradually moving this codebase to a more modern and more strongly typed style. We only make stylistic changes in code that we must touch for other reasons.

Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. Use [isort](https://pycqa.github.io/isort/) for sorting imports and [Black](https://black.readthedocs.io/en/stable/) for code formatting. Please install the pre-commit hooks to automatically format your code before committing changes.

Use full type hints, following these conventions:

- Use built-in collection types directly (e.g. `list` not `List`)
- Use union operator syntax (e.g. `str | None` not `Optional[str]`, `str | int` not `Union[str, int]`)
- Use type hints for all:
  - Function parameters and return values 
  - Class attributes
  - Local variables where helpful for clarity

### Type System

The project uses a shared type vocabulary defined in `coders/types.py`.

### Testing

The project uses [pytest](https://docs.pytest.org/en/latest/) for running unit tests. The test files are located in the `aider/tests` directory and follow the naming convention `test_*.py`.

#### Running Tests

To run the entire test suite, use the following command from the project root directory:

```
pytest
```

You can also run specific test files or test cases by providing the file path or test name:

```
pytest aider/tests/test_coder.py
pytest aider/tests/test_coder.py::TestCoder::test_specific_case
```

#### Continuous Integration

The project uses GitHub Actions for continuous integration. The testing workflows are defined in the following files:

- `.github/workflows/ubuntu-tests.yml`: Runs tests on Ubuntu for Python versions 3.10 through 3.13.
- `.github/workflows/windows-tests.yml`: Runs that on Windows

These workflows are triggered on push and pull request events to the `main` branch, ignoring changes to the `aider/website/**` and `README.md` files.

#### Docker Build and Test

The `.github/workflows/docker-build-test.yml` workflow is used to build a Docker image for the project on every push or pull request event to the `main` branch. It checks out the code, sets up Docker, logs in to DockerHub, and then builds the Docker image without pushing it to the registry.

#### Writing Tests

When contributing new features or making changes to existing code, ensure that you write appropriate tests to maintain code coverage. Follow the existing patterns and naming conventions used in the `aider/tests` directory.

If you need to mock or create test data, consider adding it to the test files or creating separate fixtures or utility functions within the `aider/tests` directory.

#### Test Requirements

The project uses `pytest` as the testing framework, which is installed as a development dependency. To install the development dependencies, run the following command:

```
pip install -r requirements-dev.txt
```

### Managing Dependencies

When introducing new dependencies, make sure to add them to the appropriate `requirements.in` file (e.g., `requirements.in` for main dependencies, `requirements-dev.in` for development dependencies). Then, run the following commands to update the corresponding `requirements.txt` file:

```
pip install pip-tools
./scripts/pip-compile.sh
```

If you want to upgrade all dependencies, use the `--upgrade` flag:

```
./scripts/pip-compile.sh --upgrade
```

Given pip's limitations, it is wise to create a fresh venv after upgrading dependencies. (And you may want to consider doing so after adding a dependency.)

## Releases

The project uses automated workflows to publish releases to both PyPI and Docker Hub. Here's how to create a new release:

### Version Numbering

Version number syntax is `brade-v[0-9]+.[0-9]+.[0-9]+`.

The project uses semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward compatible manner
- PATCH version for backward compatible bug fixes

### Creating a Release

1. Ensure all tests pass and the code is ready for release:
   ```bash
   pytest
   ```

2. Update `HISTORY.md`.

2. Create and push a version tag:
   ```bash
   # Replace X.Y.Z with the new version number
   git tag brade-vX.Y.Z
   git push origin brade-vX.Y.Z
   ```

### Automated Release Process

The release process is automated through GitHub Actions workflows:

1. PyPI Release (`.github/workflows/release.yml`):
   - Triggered by pushing a tag matching `brade-v[0-9]+.[0-9]+.[0-9]+`
   - Builds the Python package
   - Publishes to PyPI using twine

2. Docker Release (`.github/workflows/docker-release.yml`):
   - Triggered by pushing a tag matching `brade-v[0-9]+.[0-9]+.[0-9]+`
   - Builds multi-architecture Docker images (amd64, arm64)
   - Pushes to Docker Hub with version-specific and 'latest' tags

### Verifying the Release

After the workflows complete:

1. Check PyPI listing at https://pypi.org/project/brade/
   ```bash
   # Test installation from PyPI
   python -m pip install --no-cache-dir brade==${VERSION}
   ```

2. Check Docker Hub at https://hub.docker.com/r/deansher/brade
   ```bash
   # Test the Docker image
   docker pull deansher/brade:${VERSION}
   docker run --rm deansher/brade:${VERSION} --version
   ```

### Troubleshooting Releases

If a release fails:

1. Check the GitHub Actions logs for error details
2. For PyPI issues:
   - Ensure the version tag follows the correct format
   - Verify PyPI credentials are correctly set
3. For Docker issues:
   - Ensure Docker Hub credentials are correctly set
   - Check multi-architecture build configuration

### Pre-commit Hooks

The project uses [pre-commit](https://pre-commit.com/) hooks to automatically format code, lint, and run other checks before committing changes. After cloning the repository, run the following command to set up the pre-commit hooks:

```
pre-commit install
```

pre-commit will then run automatically on each `git commit` command. You can use the following command line to run pre-commit manually:

```
pre-commit run --all-files
```

## Code Architecture

The project's code is organized into several conceptual layers, from lowest to highest:

### Low-Level Support Layer
Files in `aider/` root that provide basic functionality:
- `types.py` - Type definitions widely used across the app
- `utils.py` - Basic utilities and helpers
- `io.py` - Basic I/O operations
- `dump.py` - Debugging utilities
- `exceptions.py` - Error definitions
- `llm.py` - LLM API communication
- `models.py` - LLM model definitions
- `prompts.py` - Prompts and related constants
- `brade_prompts.py` - Prompts and related constants introduced by Brade

These modules should:
- Have minimal dependencies on other project code
- Be usable independently
- Not import from higher layers

### Mid-Level Services Layer  
Files in `aider/` root that coordinate between layers:
- `sendchat.py` - LLM API communication
- `repomap.py` - Repository content mapping
- `linter.py` - Code linting services
- `repo.py` - Git repository operations 

These modules:
- May import from the support layer
- Should not import from high-level layers
- Provide services used by high-level layers

### High-Level Application Layer
Files in `aider/` root and `aider/coders/` that implement core application logic:
- `aider/coders/` - Core editing and chat functionality
- `main.py` - Application entry point and CLI
- `commands.py` - User command processing

These modules:
- May import from lower layers
- Implement the main application workflows
- Handle user interaction

### Key Architectural Principles

1. **Dependency Direction**: Modules should only import from the same or lower layers
2. **Layer Isolation**: Lower layers should not know about higher layers
3. **Interface Stability**: Lower layers should provide stable interfaces
4. **Minimal Dependencies**: Each module should have minimal dependencies

### Special Considerations for Brade

Since Brade is a fork of Aider:
- We maintain these layering principles in new code.
- We add proper layering when we must modify code anyway.
- We minimize architectural changes that would make merges harder.
- We document violations we discover but don't believe we should fix.

This helps us improve the architecture incrementally while staying close to upstream Aider.

## PyPI Project Setup for Forks

To set up the project on PyPI using OpenID Connect (OIDC):

1. Change the project name, and perhaps description, in `pyproject.toml` and `README.md`.

2. Create a PyPI account at https://pypi.org/account/register/

3. Configure PyPI trusted publisher:
   - Go to your project page on PyPI
   - Navigate to Settings > Publishing
   - Click "Add a new publisher"
   - Set the following values:
     - Publisher: GitHub Actions
     - Organization: your GitHub username or org
     - Repository: brade
     - Workflow name: release
     - Environment: (leave blank)

4. Update the release workflow:
   - Check `.github/workflows/release.yml` is properly configured
   - Ensure it includes the OIDC configuration:
     ```yaml
     permissions:
       id-token: write
     ```
   - Test with a pre-release version if needed

The OIDC approach eliminates the need to manage API tokens, providing better security through automated credential management. GitHub Actions will automatically authenticate to PyPI using your configured trusted publisher relationship.

Note: Only repository maintainers need PyPI access. Contributors can submit PRs without it.

## Docker Hub Project Setup for Forks

To set up the project on Docker Hub:

1. Create a Docker Hub account at https://hub.docker.com/signup
2. Generate an access token:
   - Go to https://hub.docker.com/settings/security
   - Click "New Access Token"
   - Give it a description and select "Read & Write" permissions
   - Save the token securely - you won't be able to see it again

3. Add Docker Hub credentials to GitHub Actions:
   - Go to your repository's Settings > Secrets and variables > Actions
   - Create two new repository secrets:
     - `DOCKERHUB_USERNAME`: Your Docker Hub username
     - `DOCKERHUB_PASSWORD`: Your Docker Hub access token

4. Update Docker-related files:
   - Modify image names in `docker/Dockerfile` if needed
   - Update Docker tags in `.github/workflows/docker-release.yml`
   - Consider updating Docker build configurations

5. Verify the Docker workflow:
   - Check `.github/workflows/docker-release.yml` is properly configured
   - Ensure the workflow uses both Docker Hub secrets
   - Test with a pre-release version if needed

Note: Only repository maintainers need Docker Hub access. Contributors can submit PRs without it.

