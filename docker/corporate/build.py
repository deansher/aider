#!/usr/bin/env python3

"""
Build script for corporate Brade Docker images.
Validates configuration and generates the final Dockerfile.
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from typing import Any, Dict

def load_config(config_path: str) -> Dict[Any, Any]:
    """Load and validate the corporate configuration."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Basic validation - expand as needed
    required_fields = ['openai-api-base', 'model']
    missing = [field for field in required_fields if field not in config]
    if missing:
        print(f"Error: Missing required fields in config: {missing}")
        sys.exit(1)
    
    return config

def generate_docker_args(config: Dict[Any, Any]) -> str:
    """Convert config into Docker command-line arguments."""
    # Only convert certain settings to command-line args
    force_args = ['openai-api-base', 'model']
    args = []
    for key in force_args:
        if key in config:
            args.append(f'--{key}')
            args.append(str(config[key]))
    return ' '.join(f'"{arg}"' for arg in args)

def main():
    parser = argparse.ArgumentParser(description='Build corporate Brade Docker image')
    parser.add_argument('--config', default='corporate-config.yml',
                      help='Path to corporate config file')
    parser.add_argument('--tag', required=True,
                      help='Tag for the built image')
    args = parser.parse_args()

    # Load and validate config
    config = load_config(args.config)
    
    # Read template
    template_path = Path(__file__).parent / 'Dockerfile.template'
    with open(template_path) as f:
        template = f.read()
    
    # Generate Docker arguments
    docker_args = generate_docker_args(config)
    
    # Create final Dockerfile
    dockerfile = template.replace('CORPORATE_ARGS_PLACEHOLDER', docker_args)
    
    # Write temporary Dockerfile
    tmp_dockerfile = 'Dockerfile.corporate'
    with open(tmp_dockerfile, 'w') as f:
        f.write(dockerfile)
    
    # Build the image
    os.system(f'docker build -f {tmp_dockerfile} -t {args.tag} .')
    
    # Cleanup
    os.remove(tmp_dockerfile)

if __name__ == '__main__':
    main()
