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
from sherpa.core.integrations.azure_devops_client import get_azure_devops_client
from sherpa.core.harness.autonomous_runner import run_autonomous_harness as run_harness_loop

console = Console()


async def run_autonomous_harness(spec_file: str, source: Optional[str] = None, max_iterations: Optional[int] = None):
    """
    Execute autonomous coding harness with spec file

    Args:
        spec_file: Path to specification file
        source: Optional source type (azure-devops, file, etc.)
        max_iterations: Optional maximum number of iterations
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

        # Generate session ID and project directory
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"
        project_dir = Path.cwd() / session_id

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
                'created_via': 'cli',
                'project_dir': str(project_dir)
            })
        }

        created_session_id = await db.create_session(session_data)

        # Log session start
        await db.add_log(
            created_session_id,
            'info',
            f'Session initialized with spec file: {spec_file}',
            json.dumps({'source': source, 'project_dir': str(project_dir)})
        )

        # Display session info
        console.print("\n[green]✓ Session created successfully![/green]")

        table = Table(title="Session Details", show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Session ID", created_session_id)
        table.add_row("Spec File", spec_file)
        table.add_row("Project Directory", str(project_dir))
        table.add_row("Status", "initializing")

        console.print(table)

        # Run autonomous harness
        console.print("\n[cyan]Starting autonomous harness with two-agent system...[/cyan]")
        console.print("[cyan]- Initializer agent will create comprehensive feature list[/cyan]")
        console.print("[cyan]- Coding agents will implement features with knowledge injection[/cyan]")
        console.print("[cyan]- Auto-continue enabled with 3s delay between iterations[/cyan]\n")

        # Run the autonomous harness loop
        await run_harness_loop(
            session_id=created_session_id,
            spec_content=spec_content,
            project_dir=project_dir,
            db=db,
            max_iterations=max_iterations,
            enable_knowledge_injection=True
        )

        console.print(f"\n[green]✓ Session {created_session_id} completed![/green]")
        console.print(f"[green]View session logs: sherpa logs {created_session_id}[/green]")
        console.print(f"[green]Project directory: {project_dir}[/green]")

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


async def run_with_azure_devops():
    """
    Execute autonomous harness with Azure DevOps work items

    Returns:
        Session ID if successful, None otherwise
    """
    db = Database()

    try:
        # Initialize database
        await db.initialize()

        # Get Azure DevOps configuration
        console.print("\n[cyan]Checking Azure DevOps configuration...[/cyan]")

        azure_org = await db.get_config('azure_devops_org')
        azure_project = await db.get_config('azure_devops_project')
        azure_pat = await db.get_config('azure_devops_pat')

        if not all([azure_org, azure_project, azure_pat]):
            console.print("\n[red]Error: Azure DevOps not configured[/red]")
            console.print("[yellow]Please configure Azure DevOps first:[/yellow]")
            console.print("  1. Go to http://localhost:3001/sources")
            console.print("  2. Fill in Azure DevOps details")
            console.print("  3. Test connection and save")
            return None

        # Connect to Azure DevOps
        console.print("[cyan]Connecting to Azure DevOps...[/cyan]")
        azure_client = get_azure_devops_client()

        try:
            connection_result = await azure_client.connect(azure_org, azure_project, azure_pat)
            console.print(f"[green]✓ {connection_result['message']}[/green]")
        except Exception as e:
            console.print(f"\n[red]Error: Failed to connect to Azure DevOps: {str(e)}[/red]")
            return None

        # Fetch work items
        console.print("\n[cyan]Fetching work items...[/cyan]")

        try:
            work_items = await azure_client.get_work_items(top=10)

            if not work_items:
                console.print("\n[yellow]No work items found[/yellow]")
                return None

            console.print(f"[green]✓ Found {len(work_items)} work items[/green]")

            # Display work items
            table = Table(title="Available Work Items")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="white")
            table.add_column("Type", style="yellow")
            table.add_column("State", style="green")

            for item in work_items[:5]:  # Show first 5
                table.add_row(
                    str(item['id']),
                    item['title'][:50] + "..." if len(item['title']) > 50 else item['title'],
                    item['type'],
                    item['state']
                )

            console.print(table)

            # Use first work item for now (in interactive mode, user would select)
            selected_work_item = work_items[0]
            work_item_id = selected_work_item['id']

            console.print(f"\n[cyan]Using work item #{work_item_id}: {selected_work_item['title']}[/cyan]")

        except Exception as e:
            console.print(f"\n[red]Error: Failed to fetch work items: {str(e)}[/red]")
            return None

        # Convert work item to spec
        console.print("\n[cyan]Converting work item to specification...[/cyan]")

        try:
            spec_content = await azure_client.convert_work_item_to_spec(work_item_id)
            console.print("[green]✓ Specification generated[/green]")

            # Save spec to temp file
            spec_path = Path.cwd() / f"spec_work_item_{work_item_id}.txt"
            spec_path.write_text(spec_content)
            console.print(f"[green]✓ Saved to {spec_path}[/green]")

        except Exception as e:
            console.print(f"\n[red]Error: Failed to convert work item: {str(e)}[/red]")
            return None

        # Generate session ID and project directory
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"
        project_dir = Path.cwd() / session_id

        # Create session in database
        console.print("\n[cyan]Creating new autonomous coding session...[/cyan]")

        session_data = {
            'id': session_id,
            'spec_file': str(spec_path.absolute()),
            'status': 'initializing',
            'total_features': 0,
            'completed_features': 0,
            'git_branch': None,
            'work_item_id': str(work_item_id),  # Link to Azure DevOps work item
            'metadata': json.dumps({
                'source': 'azure-devops',
                'azure_org': azure_org,
                'azure_project': azure_project,
                'work_item_id': work_item_id,
                'work_item_title': selected_work_item['title'],
                'work_item_type': selected_work_item['type'],
                'created_via': 'cli',
                'project_dir': str(project_dir)
            })
        }

        created_session_id = await db.create_session(session_data)

        # Log session start
        await db.add_log(
            created_session_id,
            'info',
            f'Session initialized with Azure DevOps work item #{work_item_id}',
            json.dumps({'work_item': selected_work_item, 'project_dir': str(project_dir)})
        )

        # Display session info
        console.print("\n[green]✓ Session created successfully![/green]")

        table = Table(title="Session Details", show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Session ID", created_session_id)
        table.add_row("Work Item", f"#{work_item_id}")
        table.add_row("Work Item Title", selected_work_item['title'])
        table.add_row("Spec File", str(spec_path))
        table.add_row("Project Directory", str(project_dir))
        table.add_row("Status", "initializing")

        console.print(table)

        # Run autonomous harness
        console.print("\n[cyan]Starting autonomous harness with two-agent system...[/cyan]")
        console.print("[cyan]- Initializer agent will create comprehensive feature list[/cyan]")
        console.print("[cyan]- Coding agents will implement features with knowledge injection[/cyan]")
        console.print("[cyan]- Auto-continue enabled with 3s delay between iterations[/cyan]\n")

        # Run the autonomous harness loop
        await run_harness_loop(
            session_id=created_session_id,
            spec_content=spec_content,
            project_dir=project_dir,
            db=db,
            max_iterations=None,  # Unlimited for Azure DevOps
            enable_knowledge_injection=True
        )

        console.print(f"\n[green]✓ Session {created_session_id} completed![/green]")
        console.print(f"[green]View session logs: sherpa logs {created_session_id}[/green]")
        console.print(f"[green]Project directory: {project_dir}[/green]")

        return created_session_id

    finally:
        await db.close()


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
        session_id = asyncio.run(run_with_azure_devops())

        if session_id:
            console.print(f"\n[green]✓ Session {session_id} is now running![/green]")

    else:
        console.print(f"\n[red]Error: Unknown source type: {source}[/red]")
