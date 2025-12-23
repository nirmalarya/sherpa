"""
SHERPA V1 - CLI Init Command
Initialize Bedrock KB configuration and setup
"""

import os
import json
from pathlib import Path
from typing import Optional

import boto3
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text

console = Console()


def check_aws_credentials() -> tuple[bool, Optional[str]]:
    """
    Check if AWS credentials are available

    Returns:
        Tuple of (credentials_exist, error_message)
    """
    try:
        # Try to create boto3 session
        session = boto3.Session()
        credentials = session.get_credentials()

        if credentials is None:
            return False, "No AWS credentials found. Please configure AWS CLI or set environment variables."

        # Try to get current credentials to verify they work
        try:
            sts = session.client('sts')
            sts.get_caller_identity()
            return True, None
        except Exception as e:
            return False, f"AWS credentials exist but are invalid: {str(e)}"

    except Exception as e:
        return False, f"Error checking AWS credentials: {str(e)}"


def validate_bedrock_kb(kb_id: str, region: str) -> tuple[bool, Optional[str]]:
    """
    Validate that Bedrock Knowledge Base exists and is accessible

    Args:
        kb_id: Knowledge Base ID
        region: AWS region

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        client = boto3.client('bedrock-agent', region_name=region)

        # Try to get knowledge base details
        response = client.get_knowledge_base(knowledgeBaseId=kb_id)
        kb_name = response.get('knowledgeBase', {}).get('name', 'Unknown')

        return True, f"Connected to Knowledge Base: {kb_name}"

    except client.exceptions.ResourceNotFoundException:
        return False, f"Knowledge Base '{kb_id}' not found in region '{region}'"

    except Exception as e:
        # In development/testing, we allow this to fail gracefully
        error_msg = str(e)
        if "credentials" in error_msg.lower() or "access" in error_msg.lower():
            return False, "Mock mode will be used (AWS credentials not configured)"
        return False, f"Error validating Knowledge Base: {error_msg}"


def create_config_file(kb_id: str, region: str, org_name: Optional[str] = None) -> Path:
    """
    Create configuration file with Bedrock settings

    Args:
        kb_id: Knowledge Base ID
        region: AWS region
        org_name: Optional organization name

    Returns:
        Path to created config file
    """
    # Ensure sherpa directory exists
    sherpa_dir = Path("sherpa")
    if not sherpa_dir.exists():
        # We might be in the project root or sherpa is elsewhere
        # Check if we're already in a directory with sherpa subdirectory
        current_dir = Path.cwd()
        if (current_dir / "sherpa").exists():
            sherpa_dir = current_dir / "sherpa"
        else:
            sherpa_dir = current_dir

    config_path = sherpa_dir / "config.json"

    # Load existing config if it exists
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
        except Exception:
            pass

    # Update config with Bedrock settings
    config = {
        **existing_config,
        "bedrock": {
            "knowledge_base_id": kb_id,
            "region": region,
            "enabled": True
        }
    }

    if org_name:
        config["organization"] = org_name

    # Write config file
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    return config_path


def init_command():
    """
    Initialize SHERPA configuration

    Steps:
    1. Check AWS credentials
    2. Prompt for Bedrock KB ID and region
    3. Validate connection to Bedrock
    4. Create configuration file
    5. Display success message with next steps
    """
    # Display welcome banner
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🏔️  SHERPA V1 - Initialization[/bold cyan]\n\n"
        "This wizard will help you configure SHERPA with AWS Bedrock Knowledge Base.",
        border_style="cyan"
    ))
    console.print()

    # Step 1: Check AWS credentials
    console.print("[bold]Step 1:[/bold] Checking AWS credentials...")
    credentials_ok, error_msg = check_aws_credentials()

    if not credentials_ok:
        console.print(f"[yellow]⚠️  {error_msg}[/yellow]")
        console.print("\n[dim]Note: SHERPA will run in mock mode for development/testing.[/dim]")
        console.print("[dim]To use AWS Bedrock, configure AWS CLI or set environment variables:[/dim]")
        console.print("[dim]  - AWS_ACCESS_KEY_ID[/dim]")
        console.print("[dim]  - AWS_SECRET_ACCESS_KEY[/dim]")
        console.print("[dim]  - AWS_REGION[/dim]")

        use_mock = Confirm.ask("\nContinue with mock mode?", default=True)
        if not use_mock:
            console.print("[red]Initialization cancelled.[/red]")
            return

        # Use default mock values
        kb_id = "mock-knowledge-base-id"
        region = "us-east-1"
        org_name = None
    else:
        console.print("[green]✓[/green] AWS credentials validated")
        console.print()

        # Step 2: Prompt for Bedrock configuration
        console.print("[bold]Step 2:[/bold] Configure Bedrock Knowledge Base")
        console.print()

        kb_id = Prompt.ask(
            "Knowledge Base ID",
            default="your-kb-id-here"
        )

        region = Prompt.ask(
            "AWS Region",
            default="us-east-1"
        )

        org_name = Prompt.ask(
            "Organization name (optional)",
            default=""
        )
        org_name = org_name.strip() if org_name else None

        console.print()

        # Step 3: Validate Bedrock connection
        console.print("[bold]Step 3:[/bold] Validating Bedrock Knowledge Base...")
        kb_valid, validation_msg = validate_bedrock_kb(kb_id, region)

        if not kb_valid:
            console.print(f"[yellow]⚠️  {validation_msg}[/yellow]")
            console.print("[dim]Configuration will be saved but may not work until credentials are valid.[/dim]")
        else:
            console.print(f"[green]✓[/green] {validation_msg}")

    console.print()

    # Step 4: Create configuration file
    console.print("[bold]Step 4:[/bold] Creating configuration file...")
    try:
        config_path = create_config_file(kb_id, region, org_name)
        console.print(f"[green]✓[/green] Configuration saved to: [cyan]{config_path}[/cyan]")
    except Exception as e:
        console.print(f"[red]✗[/red] Error creating configuration file: {e}")
        return

    console.print()

    # Step 5: Display success message
    success_panel = Panel.fit(
        "[bold green]✓ Initialization Complete![/bold green]\n\n"
        "SHERPA has been configured successfully.\n\n"
        "[bold]Next steps:[/bold]\n"
        "  1. Run [cyan]sherpa query \"your search terms\"[/cyan] to test Bedrock\n"
        "  2. Run [cyan]sherpa generate[/cyan] to create instruction files\n"
        "  3. Run [cyan]sherpa serve[/cyan] to start the web dashboard\n"
        "  4. Run [cyan]sherpa --help[/cyan] to see all available commands",
        border_style="green",
        title="Success"
    )
    console.print(success_panel)
    console.print()

    # Display configuration summary
    console.print("[bold]Configuration Summary:[/bold]")
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("[dim]Knowledge Base ID:[/dim]", kb_id)
    table.add_row("[dim]AWS Region:[/dim]", region)
    if org_name:
        table.add_row("[dim]Organization:[/dim]", org_name)
    table.add_row("[dim]Config File:[/dim]", str(config_path))
    console.print(table)
    console.print()
