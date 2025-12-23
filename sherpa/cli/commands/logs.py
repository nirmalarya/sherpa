"""
SHERPA V1 - CLI Logs Command
View session logs with Rich formatting and syntax highlighting
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax

from sherpa.core.logging_config import get_logger
import httpx

console = Console()
logger = get_logger("sherpa.cli.logs")

# API configuration
API_BASE_URL = "http://localhost:8001"


def logs_command(session_id: str) -> None:
    """
    View session logs with Rich formatting

    Displays:
    - Session ID
    - Chronological log entries
    - Log levels (INFO, ERROR, DEBUG, WARNING)
    - Timestamps
    - Syntax highlighting for structured logs

    Args:
        session_id: The session ID to view logs for
    """
    try:
        # Show header
        console.print()
        console.print(Panel(
            f"[bold cyan]📋 Session Logs[/bold cyan]\n\n"
            f"[dim]Session ID: {session_id}[/dim]",
            title="SHERPA Logs",
            border_style="cyan"
        ))
        console.print()

        # Run async fetch
        logs = asyncio.run(_fetch_session_logs(session_id))

        if not logs:
            console.print("[yellow]⚠️  No logs found for this session[/yellow]")
            console.print(f"\n[dim]Session ID: {session_id}[/dim]")
            console.print("[dim]Logs will appear here as the session runs[/dim]")
            return

        # Display logs
        _display_logs(logs, session_id)

    except Exception as e:
        logger.error(f"Error fetching logs: {e}", exc_info=True)
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("\n[dim]Make sure the SHERPA backend is running on port 8001[/dim]")


async def _fetch_session_logs(session_id: str) -> List[Dict[str, Any]]:
    """
    Fetch logs for a specific session from the API

    Args:
        session_id: The session ID to fetch logs for

    Returns:
        List of log dictionaries
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            with console.status(f"[cyan]Fetching logs for {session_id}...", spinner="dots"):
                response = await client.get(f"{API_BASE_URL}/api/sessions/{session_id}/logs")

                if response.status_code == 404:
                    console.print(f"[red]❌ Session not found: {session_id}[/red]")
                    return []

                if response.status_code != 200:
                    logger.error(f"API returned status {response.status_code}")
                    console.print(f"[red]❌ API error: {response.status_code}[/red]")
                    return []

                data = response.json()
                return data.get('logs', [])

    except httpx.ConnectError:
        logger.error("Could not connect to SHERPA backend")
        console.print("[red]❌ Could not connect to SHERPA backend[/red]")
        console.print("[dim]Start the backend with: sherpa serve[/dim]")
        return []
    except Exception as e:
        logger.error(f"Error fetching logs: {e}", exc_info=True)
        console.print(f"[red]❌ Error: {e}[/red]")
        return []


def _display_logs(logs: List[Dict[str, Any]], session_id: str) -> None:
    """
    Display logs in a formatted table with syntax highlighting

    Args:
        logs: List of log dictionaries
        session_id: The session ID
    """
    # Count by level
    level_counts = {
        'INFO': 0,
        'ERROR': 0,
        'WARNING': 0,
        'DEBUG': 0
    }

    for log in logs:
        level = log.get('level', 'INFO').upper()
        if level in level_counts:
            level_counts[level] += 1

    # Show summary
    console.print(f"[bold green]✅ Found {len(logs)} log entries[/bold green]\n")

    # Create logs table
    table = Table(
        title=f"📝 Logs for {session_id}",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        title_style="bold white"
    )

    table.add_column("Time", style="dim", width=20)
    table.add_column("Level", style="white", width=10)
    table.add_column("Message", style="white", min_width=50)

    for log in logs:
        timestamp = log.get('timestamp', '')
        level = log.get('level', 'INFO').upper()
        message = log.get('message', '')

        # Format timestamp
        time_display = _format_time(timestamp)

        # Format level with emoji and color
        level_display = _format_level(level)

        # Format message (truncate if too long for display)
        message_display = message
        if len(message) > 100:
            message_display = message[:97] + "..."

        # Add row to table
        table.add_row(
            time_display,
            level_display,
            message_display
        )

    console.print(table)
    console.print()

    # Show level summary
    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_column("Level", style="bold")
    summary_table.add_column("Count", justify="right")

    if level_counts['INFO'] > 0:
        summary_table.add_row("ℹ️  INFO", str(level_counts['INFO']))
    if level_counts['WARNING'] > 0:
        summary_table.add_row("⚠️  WARNING", str(level_counts['WARNING']))
    if level_counts['ERROR'] > 0:
        summary_table.add_row("❌ ERROR", str(level_counts['ERROR']))
    if level_counts['DEBUG'] > 0:
        summary_table.add_row("🐛 DEBUG", str(level_counts['DEBUG']))

    console.print(Panel(
        summary_table,
        title="[bold white]📊 Log Level Summary[/bold white]",
        border_style="dim"
    ))


def _format_level(level: str) -> str:
    """
    Format log level with emoji and color

    Args:
        level: Log level string

    Returns:
        Formatted level string with emoji and color
    """
    level_map = {
        'INFO': '[cyan]ℹ️  INFO[/cyan]',
        'WARNING': '[yellow]⚠️  WARN[/yellow]',
        'ERROR': '[red]❌ ERROR[/red]',
        'DEBUG': '[dim]🐛 DEBUG[/dim]'
    }
    return level_map.get(level, f'[dim]{level}[/dim]')


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
            seconds = delta.seconds % 60

            if hours > 0:
                return f"{hours}h {minutes}m ago"
            elif minutes > 0:
                return f"{minutes}m ago"
            else:
                return f"{seconds}s ago"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        else:
            # Show date and time for older logs
            return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        # Fallback to showing just the date/time part
        try:
            return timestamp[:19].replace('T', ' ')
        except:
            return timestamp[:10]
