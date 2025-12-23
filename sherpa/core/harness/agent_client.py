"""
SHERPA V1 - Agent Client
Claude Agent SDK client configuration for autonomous coding
"""

import json
import os
from pathlib import Path
from typing import Optional

try:
    from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient
    from claude_code_sdk.types import HookMatcher
    CLAUDE_SDK_AVAILABLE = True
except ImportError:
    CLAUDE_SDK_AVAILABLE = False


# Puppeteer MCP tools for browser automation
PUPPETEER_TOOLS = [
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    "mcp__puppeteer__puppeteer_click",
    "mcp__puppeteer__puppeteer_fill",
    "mcp__puppeteer__puppeteer_select",
    "mcp__puppeteer__puppeteer_hover",
    "mcp__puppeteer__puppeteer_evaluate",
]

# Built-in tools
BUILTIN_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
]


def bash_security_hook(context):
    """
    Security hook for Bash command validation.
    Validates commands against allowlist before execution.
    """
    # Allowed commands for autonomous coding
    ALLOWED_COMMANDS = [
        'ls', 'cat', 'grep', 'wc', 'head', 'tail',
        'git', 'npm', 'node', 'npx',
        'mkdir', 'touch', 'cp', 'mv', 'rm',
        'chmod', 'pwd', 'which', 'whoami',
        'curl', 'wget',
        'python', 'python3', 'pip', 'pip3',
        'uvicorn', 'pytest', 'ruff', 'pyright',
        'lsof', 'ps', 'kill', 'sleep',
        'jq', 'sed', 'awk', 'sort', 'uniq',
    ]

    command = context.get("command", "")
    if not command:
        return

    # Extract the first word (command name)
    command_name = command.strip().split()[0] if command.strip() else ""

    # Check if command is in allowlist
    if command_name and command_name not in ALLOWED_COMMANDS:
        raise ValueError(
            f"Command '{command_name}' is not in the allowlist. "
            f"Allowed commands: {', '.join(ALLOWED_COMMANDS)}"
        )


def create_agent_client(
    project_dir: Path,
    model: str = "claude-sonnet-4.5",
    system_prompt: Optional[str] = None
) -> Optional[object]:
    """
    Create a Claude Agent SDK client for autonomous coding.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        system_prompt: Custom system prompt (with knowledge injection)

    Returns:
        Configured ClaudeSDKClient or None if SDK not available

    Security layers (defense in depth):
    1. Sandbox - OS-level bash command isolation
    2. Permissions - File operations restricted to project_dir only
    3. Security hooks - Bash commands validated against allowlist
    """
    if not CLAUDE_SDK_AVAILABLE:
        return None

    oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not oauth_token:
        raise ValueError(
            "CLAUDE_CODE_OAUTH_TOKEN environment variable not set.\n"
            "Generate your OAuth token using: claude setup-token\n"
            "Then set: export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token-here'"
        )

    # Default system prompt if not provided
    if system_prompt is None:
        system_prompt = "You are an expert full-stack developer building a production-quality web application."

    # Create comprehensive security settings
    security_settings = {
        "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
        "permissions": {
            "defaultMode": "acceptEdits",
            "allow": [
                # Allow all file operations within project directory
                "Read(./**)",
                "Write(./**)",
                "Edit(./**)",
                "Glob(./**)",
                "Grep(./**)",
                # Bash permission with security hook validation
                "Bash(*)",
                # Allow Puppeteer MCP tools
                *PUPPETEER_TOOLS,
            ],
        },
    }

    # Ensure project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write settings to project directory
    settings_file = project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            system_prompt=system_prompt,
            allowed_tools=[
                *BUILTIN_TOOLS,
                *PUPPETEER_TOOLS,
            ],
            mcp_servers={
                "puppeteer": {"command": "npx", "args": ["puppeteer-mcp-server"]}
            },
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
                ],
            },
            max_turns=1000,
            cwd=str(project_dir.resolve()),
            settings=str(settings_file.resolve()),
        )
    )
