# Plan for Creating a Self-Contained AppImage Distribution

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

- (✓) Subtask
  - (✓) Subsubtask
- ( ) Another subtask
```

## Requirements

We need to create a self-contained AppImage distribution that can be used in Linux environments with:

- Limited or no ability to install system packages
- Strict security policies around software installation
- Requirements for reproducible builds
- Need for offline installation capability
- Support for multiple Linux distributions

The AppImage should:
- Include all required Python dependencies
- Bundle necessary system libraries
- Work consistently across supported Linux distributions
- Not require external network access during runtime
- Support both x86_64 and aarch64 architectures

### Python and Python Package Versions

We'll use Python 3.13.0.

### First Linux Target

For initial development and testing, we'll target this Linux environment:

=== System Architecture ===
x86_64

=== Distribution Info ===
PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.5 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=jammy

=== GLIBC Version ===
ldd (Ubuntu GLIBC 2.35-0ubuntu3.8) 2.35

=== Dynamic Linker Info ===
lrwxrwxrwx 1 root root 42 May  6  2024 /lib64/ld-linux-x86-64.so.2 -> /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2

=== CPU Info ===
Architecture:                       x86_64
CPU op-mode(s):                     32-bit, 64-bit
Byte Order:                         Little Endian

## (✓) Analyze Current System Dependencies

### (✓) Identify Required System Libraries
- (✓) List all dynamic library dependencies
- (✓) Determine minimum glibc version requirements
- (✓) Document distribution-specific package names

Key findings:
- Base system requires glibc 2.35 or newer
- Core libraries needed: libssl, libcrypto, libpython3.13
- Distribution packages identified in Dockerfile
- Dynamic library dependencies handled via copy_dependencies() function

### (✓) Analyze Python Environment

#### Findings

Version Constraints by Rationale:

1. Python Version:
   - We are targeting Python 3.13 only for the AppImage distribution
   - This allows us to remove legacy compatibility constraints
   - Can use latest versions of packages that require Python 3.13

2. Package Compatibility:
   - numpy<2: Required by sentence-transformers
   - tokenizers==0.19.1: Required to resolve sentence-transformers dependencies
   - watchdog<5: Required by streamlit 1.38.0

3. Version Conflicts:
   - greenlet==3.0.3: Pinned to resolve conflict between requirements-help and requirements-playwright
   - This conflict must be handled consistently in the AppImage build

Our requirements structure consists of:

1. Base requirements.txt file containing core dependencies
2. Specialized requirement files in requirements/ directory:
   - requirements-help.txt: LLM/embedding dependencies
   - requirements-browser.txt: Streamlit UI dependencies  
   - requirements-playwright.txt: Browser automation
   - requirements-dev.txt: Development tools

Key Dependency Relationships:
- All specialized requirements files use -c ../requirements.txt constraint
- Requirements compiled with pip-tools for reproducibility
- Dynamic dependencies handled via setuptools in pyproject.toml
- No circular dependencies detected

Version Constraints by Rationale:

1. Python Version Compatibility:
   - tree-sitter==0.21.3: Later versions break tree-sitter-languages
   - importlib-metadata<8.0.0: GitHub Release action compatibility

2. Package Compatibility:
   - numpy<2: Required by sentence-transformers
   - tokenizers==0.19.1: Required to resolve sentence-transformers dependencies
   - watchdog<5: Required by streamlit 1.38.0

3. Version Conflicts:
   - greenlet==3.0.3: Pinned to resolve conflict between requirements-help and requirements-playwright

Tasks:
- (✓) Review current dependency management
- ( ) Verify all dependencies are compatible with Python 3.13
- ( ) Identify any dependencies with native extensions that need special handling
- ( ) Document any dependencies that require system libraries
- ( ) Identify platform-specific packages and their AppImage implications
- ( ) Document build-time dependencies needed for AppImage creation
- ( ) Analyze compiled extensions that need special handling in AppImage

## (✓) Design Docker-Based Build Process

### (✓) Choose Build Environment Strategy
Using Docker for AppImage builds because:
1. Enables development on non-Linux systems (e.g. Mac)
2. Provides reproducible builds via version controlled Dockerfile
3. Can be used in GitHub Actions for releases
4. Ensures consistent build environment

Implementation complete in docker/appimage-builder/Dockerfile with:
- Ubuntu 22.04 base image
- Python 3.13 from deadsnakes PPA
- AppImage tools and build dependencies
- Automated build script

### (✓) Create Basic AppImage Structure
- (✓) Define AppDir layout
- (✓) Create entry point script
- (✓) Set up environment variables

Implementation complete in scripts/build_appimage.sh with:
- Standard AppDir hierarchy
- Python venv in usr/python
- Environment setup in AppRun script
- Desktop integration files

### (✓) Package Python Environment
- (✓) Bundle Python interpreter
- (✓) Include site-packages
- (✓) Handle compiled extensions

Implementation complete with:
- Python 3.13 interpreter bundled
- Dependencies installed via pip
- Site-packages included in venv
- Native extensions handled via copy_dependencies

### (✓) System Library Management
- (✓) Identify required libraries
- (✓) Copy dependencies
- (✓) Set up runtime paths

Implementation complete with:
- Automatic library dependency detection
- Library copying via ldd analysis
- LD_LIBRARY_PATH configured in AppRun

## ( ) Implement Build Automation

### ( ) Local Build Script
- ( ) Create build environment
- ( ) Install dependencies
- ( ) Generate AppImage

### (✓) Testing Framework

#### (✓) Local Testing Procedures
- (✓) Basic smoke tests (--version, --help)
- (✓) Core functionality tests
- (✓) Help system verification
- (✓) Browser feature testing

#### (✓) Distribution Testing
- (✓) Ubuntu 22.04 compatibility
- (✓) Debian 11 validation
- (✓) Fedora 37 testing
- (✓) CentOS 8 verification

#### (✓) System Library Verification
- (✓) Library dependency checking with ldd
- (✓) Missing dependency verification
- (✓) Extracted AppImage validation

## ( ) Multi-Architecture Support

### ( ) Build Infrastructure
- ( ) Configure QEMU for cross-architecture builds
- ( ) Add aarch64 support to Dockerfile
  - ( ) Install appropriate toolchain
  - ( ) Configure cross-compilation environment
- ( ) Update build_appimage.sh for multi-arch
  - ( ) Add architecture detection
  - ( ) Handle arch-specific dependencies
  - ( ) Implement conditional library copying

### ( ) Testing Infrastructure
- ( ) Set up aarch64 test environment
  - ( ) Configure QEMU-based testing
  - ( ) Add ARM64 Docker containers
- ( ) Create architecture test matrix
  - ( ) Ubuntu 22.04 ARM64
  - ( ) Debian 11 ARM64
  - ( ) Fedora 37 ARM64
- ( ) Implement automated arch testing

## ( ) Production Release Process

### ( ) GitHub Actions Integration
- ( ) Create release workflow
  - ( ) Trigger on version tags
  - ( ) Build AppImages for all architectures
  - ( ) Run test suite on built AppImages
  - ( ) Generate checksums
- ( ) Implement version management
  - ( ) Extract version from pyproject.toml
  - ( ) Tag releases automatically
  - ( ) Update changelog

### ( ) Release Distribution
- ( ) Configure GPG signing
  - ( ) Set up signing keys in GitHub secrets
  - ( ) Implement AppImage signing step
- ( ) Create release artifacts
  - ( ) Generate SHA256 checksums
  - ( ) Package documentation
  - ( ) Include release notes
- ( ) Implement GitHub release publishing

## ( ) Documentation

### ( ) User Documentation
- ( ) Installation Guide
  - ( ) System requirements
  - ( ) Download instructions
  - ( ) Installation verification
  - ( ) Common issues and solutions
- ( ) Runtime Guide
  - ( ) Environment setup
  - ( ) Command-line options
  - ( ) Feature documentation
- ( ) Troubleshooting Guide
  - ( ) Known issues
  - ( ) Distribution-specific notes
  - ( ) Library compatibility

### ( ) Developer Documentation
- ( ) Build Environment Setup
  - ( ) Docker configuration
  - ( ) Local development setup
  - ( ) Testing environment
- ( ) Build Process Guide
  - ( ) AppImage creation steps
  - ( ) Multi-arch builds
  - ( ) Testing procedures
- ( ) Release Process
  - ( ) Version management
  - ( ) Release checklist
  - ( ) Distribution procedures
