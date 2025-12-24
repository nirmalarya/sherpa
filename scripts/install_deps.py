#!/usr/bin/env python3
"""
Simple script to install CLI dependencies
"""
import subprocess
import sys

def install_packages():
    """Install required packages"""
    packages = [
        "click==8.1.7",
        "rich==13.7.0"
    ]

    pip_path = "./venv-312/bin/pip"

    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([pip_path, "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
            sys.exit(1)

    print("\n✓ All dependencies installed successfully!")

if __name__ == "__main__":
    install_packages()
