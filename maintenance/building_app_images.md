# Building AppImages

This document describes how to build AppImage distributions of Brade.

## Prerequisites

- Docker Desktop installed and running
- Git clone of the Brade repository
- Basic familiarity with Docker and shell commands

## Build Process

### 1. Build the Docker Image

First, build the Docker image that will be used to create the AppImage:

```bash
docker build -t brade-appimage-builder -f docker/appimage-builder/Dockerfile .
```

### 2. Create AppImage Build Environment

Run the Docker container with appropriate volume mounts:

```bash
docker run --rm -it \
  -v "$(pwd):/src" \
  -v "$(pwd)/build:/build" \
  brade-appimage-builder
```

### 3. Build the AppImage

Inside the container:

```bash
cd /build
python3.13 -m pip install -e /src
./build_appimage.sh
```

The AppImage will be created in the `build` directory.

## Testing Locally

1. Make the AppImage executable:
   ```bash
   chmod +x Brade-x86_64.AppImage
   ```

2. Run basic smoke tests:
   ```bash
   ./Brade-x86_64.AppImage --version
   ./Brade-x86_64.AppImage --help
   ```

3. Test core functionality:
   ```bash
   ./Brade-x86_64.AppImage /path/to/test/files
   ```

## Architecture Support

Currently supports:
- x86_64 (amd64)

Planned support:
- aarch64 (arm64)

## CI/CD Integration

The AppImage build process is integrated into our GitHub Actions workflows:

1. Triggered on new releases
2. Builds AppImages for supported architectures
3. Attaches AppImages to GitHub releases
4. Runs automated tests on the built AppImages

See `.github/workflows/release.yml` for implementation details.

## Troubleshooting

Common issues and solutions:

1. Missing system libraries
   - Check the build logs for missing .so files
   - Add required packages to the Dockerfile

2. Runtime errors
   - Use `--appimage-extract` to inspect contents
   - Check library dependencies with `ldd`

## References

- [AppImage Documentation](https://docs.appimage.org/)
- [Design Documentation](../design-docs/app_image/plan_app_image.md)
