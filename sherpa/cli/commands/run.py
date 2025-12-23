"""
SHERPA V1 - Run Command
Execute autonomous harness with knowledge injection
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from sherpa.core.db import Database

console = Console()


async def run_autonomous_harness(spec_file: str, source: Optional[str] = None):
    """
    Execute autonomous coding harness with spec file

    Args:
        spec_file: Path to specification file
        source: Optional source type (azure-devops, file, etc.)
    """
    db = Database()

    try:
        # Initialize database
        await db.initialize()

        # Read spec file
        spec_path = Path(spec_file)
        if not spec_path.exists():
            console.print(f"[red]Error: Spec file not found: {spec_file}[/red]")
            return None

        spec_content = spec_path.read_text()

        # Generate session ID
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"

        # Create session in database
        console.print("\n[cyan]Creating new autonomous coding session...[/cyan]")

        session_data = {
            'id': session_id,
            'spec_file': str(spec_path.absolute()),
            'status': 'initializing',
            'total_features': 0,
            'completed_features': 0,
            'git_branch': None,
            'work_item_id': None,
            'metadata': json.dumps({
                'source': source,
                'spec_length': len(spec_content),
                'created_via': 'cli'
            })
        }

        created_session_id = await db.create_session(session_data)

        # Log session start
        await db.add_log(
            created_session_id,
            'info',
            f'Session initialized with spec file: {spec_file}',
            json.dumps({'source': source})
        )

        # Generate feature_list.json
        console.print("[cyan]Generating feature list...[/cyan]")
        feature_list = await generate_feature_list(spec_content, created_session_id)

        # Save feature_list.json to current directory
        feature_list_path = Path.cwd() / "feature_list.json"
        feature_list_path.write_text(json.dumps(feature_list, indent=2))

        # Update session with feature count
        await db.update_session(created_session_id, {
            'total_features': len(feature_list),
            'status': 'active'
        })

        # Log feature list generation
        await db.add_log(
            created_session_id,
            'info',
            f'Feature list generated with {len(feature_list)} features',
            json.dumps({'feature_list_path': str(feature_list_path)})
        )

        # Display session info
        console.print("\n[green]✓ Session created successfully![/green]")

        table = Table(title="Session Details", show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Session ID", created_session_id)
        table.add_row("Spec File", spec_file)
        table.add_row("Status", "active")
        table.add_row("Total Features", str(len(feature_list)))
        table.add_row("Feature List", str(feature_list_path))

        console.print(table)

        # Simulate initializer agent start
        console.print("\n[cyan]Starting initializer agent...[/cyan]")
        await db.add_log(
            created_session_id,
            'info',
            'Initializer agent started',
            json.dumps({'agent_type': 'initializer'})
        )

        console.print("\n[yellow]Note: Full autonomous harness execution not yet implemented.[/yellow]")
        console.print("[yellow]Session created and tracked in database.[/yellow]")
        console.print(f"\n[green]View session status: sherpa status[/green]")
        console.print(f"[green]View session logs: sherpa logs {created_session_id}[/green]")

        return created_session_id

    finally:
        await db.close()


async def generate_feature_list(spec_content: str, session_id: str) -> list:
    """
    Generate feature list from spec file

    For now, this creates a basic feature list.
    In the future, this will use AI to parse the spec and generate comprehensive features.

    Args:
        spec_content: Content of the specification file
        session_id: Session ID for tracking

    Returns:
        List of feature dictionaries
    """
    # Basic feature extraction
    # In production, this would use AI to parse the spec intelligently

    features = [
        {
            "category": "functional",
            "description": "Initialize project structure from specification",
            "steps": [
                "Step 1: Parse specification file",
                "Step 2: Create project directories",
                "Step 3: Initialize git repository",
                "Step 4: Setup basic configuration files"
            ],
            "passes": False
        },
        {
            "category": "functional",
            "description": "Implement core features from specification",
            "steps": [
                "Step 1: Identify core requirements",
                "Step 2: Implement backend features",
                "Step 3: Implement frontend features",
                "Step 4: Test core functionality"
            ],
            "passes": False
        },
        {
            "category": "testing",
            "description": "Create test suite for implementation",
            "steps": [
                "Step 1: Setup testing framework",
                "Step 2: Write unit tests",
                "Step 3: Write integration tests",
                "Step 4: Verify all tests pass"
            ],
            "passes": False
        }
    ]

    # Add metadata about the spec
    features.append({
        "category": "metadata",
        "description": f"Session metadata - {session_id}",
        "steps": [
            f"Step 1: Spec file length: {len(spec_content)} characters",
            "Step 2: Features generated automatically",
            "Step 3: Ready for autonomous execution"
        ],
        "passes": False
    })

    return features


def run_command(spec: Optional[str] = None, source: Optional[str] = None):
    """
    CLI command handler for 'sherpa run'

    Args:
        spec: Path to specification file
        source: Source type (azure-devops, file, etc.)
    """
    console.print(Panel.fit(
        "[bold cyan]🏔️  SHERPA V1 - Autonomous Harness[/bold cyan]\n"
        "Execute autonomous coding with knowledge injection",
        border_style="cyan"
    ))

    if not spec and not source:
        console.print("\n[red]Error: Must provide either --spec or --source[/red]")
        console.print("[yellow]Usage:[/yellow]")
        console.print("  sherpa run --spec <file.txt>")
        console.print("  sherpa run --source azure-devops")
        return

    if spec and source:
        console.print("\n[yellow]Warning: Both --spec and --source provided. Using --spec.[/yellow]")

    if spec:
        # Run with spec file
        session_id = asyncio.run(run_autonomous_harness(spec, source))

        if session_id:
            console.print(f"\n[green]✓ Session {session_id} is now running![/green]")

    elif source == "azure-devops":
        # Run with Azure DevOps source
        console.print("\n[yellow]Azure DevOps source integration not yet implemented[/yellow]")
        console.print("[yellow]Coming in a future release![/yellow]")

    else:
        console.print(f"\n[red]Error: Unknown source type: {source}[/red]")
