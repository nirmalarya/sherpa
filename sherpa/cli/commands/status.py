"""
SHERPA V1 - CLI Status Command
Show active coding sessions with progress and status
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn

from sherpa.core.logging_config import get_logger
import httpx

console = Console()
logger = get_logger("sherpa.cli.status")

# API configuration
API_BASE_URL = "http://localhost:8001"


def status_command() -> None:
    """
    Show active coding sessions with progress and status

    Displays:
    - Session ID
    - Status (active/complete/error/paused)
    - Features completed / total
    - Progress percentage
    - Started time
    """
    try:
        # Show header
        console.print()
        console.print(Panel(
            "[bold cyan]📊 Active Coding Sessions[/bold cyan]\n\n"
            "[dim]Showing all sessions with their current status and progress[/dim]",
            title="SHERPA Status",
            border_style="cyan"
        ))
        console.print()

        # Run async fetch
        sessions = asyncio.run(_fetch_sessions())

        if not sessions:
            console.print("[yellow]⚠️  No sessions found[/yellow]")
            console.print("\n[dim]Start a new session with 'sherpa run' or create one in the dashboard[/dim]")
            return

        # Display sessions
        _display_sessions(sessions)

    except Exception as e:
        logger.error(f"Error fetching session status: {e}", exc_info=True)
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("\n[dim]Make sure the SHERPA backend is running on port 8001[/dim]")


async def _fetch_sessions() -> List[Dict[str, Any]]:
    """
    Fetch all sessions from the API

    Returns:
        List of session dictionaries
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            with console.status("[cyan]Fetching sessions...", spinner="dots"):
                response = await client.get(f"{API_BASE_URL}/api/sessions")

                if response.status_code != 200:
                    logger.error(f"API returned status {response.status_code}")
                    return []

                data = response.json()
                return data.get('data', {}).get('sessions', [])

    except httpx.ConnectError:
        logger.error("Could not connect to SHERPA backend")
        console.print("[red]❌ Could not connect to SHERPA backend[/red]")
        console.print("[dim]Start the backend with: sherpa serve[/dim]")
        return []
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}", exc_info=True)
        return []


def _display_sessions(sessions: List[Dict[str, Any]]) -> None:
    """
    Display sessions in a formatted table

    Args:
        sessions: List of session dictionaries
    """
    # Count by status
    status_counts = {
        'active': 0,
        'complete': 0,
        'error': 0,
        'paused': 0
    }

    for session in sessions:
        status = session.get('status', 'unknown')
        if status in status_counts:
            status_counts[status] += 1

    # Show summary
    console.print(f"[bold green]✅ Found {len(sessions)} session(s)[/bold green]\n")

    # Create sessions table
    table = Table(
        title="📋 Sessions List",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title_style="bold white"
    )

    table.add_column("Session ID", style="cyan", no_wrap=True, width=20)
    table.add_column("Status", style="white", width=12)
    table.add_column("Progress", style="white", width=30)
    table.add_column("Features", style="yellow", width=12, justify="center")
    table.add_column("Started", style="dim", width=20)

    for session in sessions:
        session_id = session.get('id', 'unknown')
        status = session.get('status', 'unknown')
        completed = session.get('completed_features', 0)
        total = session.get('total_features', 0)
        started = session.get('started_at', '')

        # Format status with emoji and color
        status_display = _format_status(status)

        # Calculate progress percentage
        if total > 0:
            progress_pct = (completed / total) * 100
            progress_bar = _create_progress_bar(progress_pct)
            progress_text = f"{progress_bar} {progress_pct:.1f}%"
        else:
            progress_text = "[dim]Not started[/dim]"

        # Format features count
        features_text = f"{completed}/{total}"

        # Format started time
        started_display = _format_time(started)

        # Add row to table
        table.add_row(
            session_id[:20],
            status_display,
            progress_text,
            features_text,
            started_display
        )

    console.print(table)
    console.print()

    # Show status summary
    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Count", justify="right")

    if status_counts['active'] > 0:
        summary_table.add_row("🟢 Active", str(status_counts['active']))
    if status_counts['complete'] > 0:
        summary_table.add_row("✅ Complete", str(status_counts['complete']))
    if status_counts['paused'] > 0:
        summary_table.add_row("⏸️  Paused", str(status_counts['paused']))
    if status_counts['error'] > 0:
        summary_table.add_row("❌ Error", str(status_counts['error']))

    console.print(Panel(
        summary_table,
        title="[bold white]📊 Status Summary[/bold white]",
        border_style="dim"
    ))


def _format_status(status: str) -> str:
    """
    Format status with emoji and color

    Args:
        status: Session status string

    Returns:
        Formatted status string with emoji and color
    """
    status_map = {
        'active': '[green]🟢 Active[/green]',
        'complete': '[blue]✅ Complete[/blue]',
        'error': '[red]❌ Error[/red]',
        'paused': '[yellow]⏸️  Paused[/yellow]',
        'stopped': '[orange]⏹️  Stopped[/orange]'
    }
    return status_map.get(status, f'[dim]{status}[/dim]')


def _create_progress_bar(percentage: float) -> str:
    """
    Create a text-based progress bar

    Args:
        percentage: Progress percentage (0-100)

    Returns:
        Formatted progress bar string
    """
    bar_width = 20
    filled = int((percentage / 100) * bar_width)
    empty = bar_width - filled

    # Choose color based on progress
    if percentage >= 100:
        color = "green"
    elif percentage >= 75:
        color = "cyan"
    elif percentage >= 50:
        color = "yellow"
    else:
        color = "red"

    bar = f"[{color}]{'█' * filled}{'░' * empty}[/{color}]"
    return bar


def _format_time(timestamp: str) -> str:
    """
    Format timestamp for display

    Args:
        timestamp: ISO format timestamp string

    Returns:
        Formatted time string
    """
    if not timestamp:
        return "[dim]Unknown[/dim]"

    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        delta = now - dt

        # Format as relative time if recent
        if delta.days == 0:
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}m ago"
            elif minutes > 0:
                return f"{minutes}m ago"
            else:
                return "Just now"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        else:
            return dt.strftime("%Y-%m-%d")
    except Exception:
        return timestamp[:10]  # Just show date part
