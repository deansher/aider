# Building AppImages

This document describes how to build AppImage distributions of Brade.

## Prerequisites

- Docker Desktop installed and running
- Git clone of the Brade repository
- Basic familiarity with Docker and shell commands
- At least 2GB free disk space

## Build Process

### 1. AppDir Structure

The AppImage is built using the following directory structure:

```
AppDir/
├── AppRun                 # Entry point script
├── brade.desktop         # Desktop integration file
├── brade.png            # Application icon
├── usr/
│   ├── bin/             # Executable scripts
│   ├── lib/             # System libraries
│   ├── python/          # Python installation
│   └── share/           # Application data
└── .DirIcon            # Symlink to brade.png
```

### 2. Build Script Details

The `build_appimage.sh` script performs these steps:

```bash
#!/bin/bash
set -e

# Create AppDir structure
mkdir -p AppDir/usr/{bin,lib,python,share}

# Install Python and dependencies
python3.13 -m venv AppDir/usr/python
source AppDir/usr/python/bin/activate
pip install --no-cache-dir -e /src[help,browser]

# Copy system libraries
copy_dependencies() {
    ldd "$1" | grep "=> /" | awk '{print $3}' | xargs -I '{}' cp -v '{}' AppDir/usr/lib/
}

# Copy Python binary and its dependencies
cp $(which python3.13) AppDir/usr/bin/
copy_dependencies $(which python3.13)

# Create entry point script
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
HERE=$(dirname "$(readlink -f "${0}")")
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONHOME="${HERE}/usr/python"
export PYTHONPATH="${HERE}/usr/python/lib/python3.13/site-packages"
exec "${HERE}/usr/bin/python3.13" -m brade "$@"
EOF
chmod +x AppDir/AppRun

# Create desktop file
cat > AppDir/brade.desktop << EOF
[Desktop Entry]
Name=Brade
Exec=brade
Icon=brade
Type=Application
Categories=Development;
EOF

# Generate AppImage
ARCH=$(uname -m) appimagetool AppDir/
```

### 3. Build the Docker Image

First, build the Docker image that will be used to create the AppImage:

```bash
docker build -t brade-appimage-builder -f docker/appimage-builder/Dockerfile .
```

### 4. Create AppImage Build Environment

Run the Docker container with appropriate volume mounts:

```bash
docker run --rm -it \
  -v "$(pwd):/src" \
  -v "$(pwd)/build:/build" \
  brade-appimage-builder
```

### 5. Build the AppImage

Inside the container:

```bash
cd /build
python3.13 -m pip install -e /src
./build_appimage.sh
```

The AppImage will be created in the `build` directory.

## Testing Procedures

### 1. Local Testing

First, make the AppImage executable:
```bash
chmod +x Brade-x86_64.AppImage
```

#### Basic Smoke Tests
```bash
./Brade-x86_64.AppImage --version
./Brade-x86_64.AppImage --help
```

#### Functionality Tests
```bash
# Test core functionality
./Brade-x86_64.AppImage /path/to/test/files

# Test help system
./Brade-x86_64.AppImage --test-help-system

# Test browser features
./Brade-x86_64.AppImage --test-browser
```

### 2. Distribution Testing

Test on different Linux distributions using Docker:

```bash
# Ubuntu 22.04
docker run --rm -v ./Brade-x86_64.AppImage:/app/brade -w /app ubuntu:22.04 ./brade --version

# Debian 11
docker run --rm -v ./Brade-x86_64.AppImage:/app/brade -w /app debian:11 ./brade --version

# Fedora 37
docker run --rm -v ./Brade-x86_64.AppImage:/app/brade -w /app fedora:37 ./brade --version

# CentOS 8
docker run --rm -v ./Brade-x86_64.AppImage:/app/brade -w /app centos:8 ./brade --version
```

### 3. System Library Verification

Check library dependencies:
```bash
ldd Brade-x86_64.AppImage
```

Verify no missing dependencies:
```bash
./Brade-x86_64.AppImage --appimage-extract
ldd squashfs-root/usr/bin/*
ldd squashfs-root/usr/lib/*
```

## Architecture Support

Currently supports:
- x86_64 (amd64)
  - Tested on glibc 2.31+
  - Compatible with most modern Linux distributions

Planned support:
- aarch64 (arm64)
  - In development
  - Will require separate build pipeline
  - Testing needed on various ARM devices

## CI/CD Integration

The AppImage build process is integrated into our GitHub Actions workflows:

1. Triggered on new releases
2. Builds AppImages for supported architectures
3. Attaches AppImages to GitHub releases
4. Runs automated tests on the built AppImages

See `.github/workflows/release.yml` for implementation details.

## Troubleshooting

### Common Issues and Solutions

1. Missing System Libraries
   - Check build logs for missing .so files
   - Add required packages to Dockerfile
   - Use `ldd` to identify missing dependencies
   - Common missing libraries:
     - libssl.so.1.1
     - libcrypto.so.1.1
     - libpython3.13.so.1.0

2. Runtime Errors
   - Use `--appimage-extract` to inspect contents
   - Check library dependencies with `ldd`
   - Verify Python environment variables
   - Common problems:
     - PYTHONPATH not set correctly
     - Missing or incompatible SSL libraries
     - glibc version conflicts

3. Distribution Compatibility
   - Test on older distributions first
   - Use `objdump -p` to check glibc requirements
   - Bundle critical libraries when needed
   - Consider static linking for problematic dependencies

4. Build Environment Issues
   - Clear Docker build cache
   - Verify Docker resource limits
   - Check disk space requirements
   - Ensure network access for dependencies

## References

- [AppImage Documentation](https://docs.appimage.org/)
- [Design Documentation](../design-docs/app_image/plan_app_image.md)
- [Python Packaging Guide](https://packaging.python.org/)
- [Docker Documentation](https://docs.docker.com/)
