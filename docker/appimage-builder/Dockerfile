# Base image
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic build tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    file \
    git \
    ldd \
    libffi-dev \
    libssl-dev \
    patchelf \
    pkg-config \
    strace \
    wget \
    zlib1g-dev \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add deadsnakes PPA and install Python 3.13
RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.13 python3.13-dev python3.13-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip and upgrade it
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13 \
    && python3.13 -m pip install --upgrade pip setuptools wheel

# Install AppImage tools
RUN wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O /usr/local/bin/appimagetool \
    && chmod +x /usr/local/bin/appimagetool

# Install Python packaging tools
RUN python3.13 -m pip install \
    pip-tools \
    wheel \
    setuptools

# Create working directory
WORKDIR /build

# Default command
CMD ["/bin/bash"]
