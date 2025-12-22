"""
SHERPA V1 - Autonomous Coding Orchestrator
Setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sherpa",
    version="1.0.0",
    author="SHERPA Development Team",
    description="Autonomous Coding Orchestrator with Knowledge Injection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sherpa",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sherpa=sherpa.cli.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "sherpa": [
            "snippets/**/*",
        ],
    },
)
