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

# Install Python 3.13.0
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz \
    && tar xzf Python-3.13.0.tgz \
    && cd Python-3.13.0 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make install \
    && cd .. \
    && rm -rf Python-3.13.0 Python-3.13.0.tgz

# Install pip and upgrade it
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13 \
    && python3.13 -m pip install --upgrade pip

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
