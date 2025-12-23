"""
SHERPA V1 - CLI Main Entry Point
Beautiful CLI with Click and Rich formatting
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🏔️  SHERPA V1 - Autonomous Coding Orchestrator

    Enhance autonomous coding agents with organizational knowledge.
    """
    pass


@cli.command()
def init():
    """Initialize Bedrock KB configuration and setup"""
    from sherpa.cli.commands.init import init_command
    init_command()


@cli.command()
def generate():
    """Create instruction files for interactive agents"""
    from sherpa.cli.commands.generate import generate_command
    generate_command()


@cli.command()
@click.option("--spec", type=click.Path(exists=True), help="Path to specification file")
@click.option("--source", type=str, help="Source type (azure-devops, file, etc.)")
def run(spec, source):
    """Execute autonomous harness"""
    console.print("[yellow]Command 'run' not yet implemented[/yellow]")


@cli.command()
@click.argument("query_text")
def query(query_text):
    """Search Bedrock Knowledge Base for snippets"""
    console.print(f"[yellow]Command 'query' not yet implemented for: {query_text}[/yellow]")


@cli.group()
def snippets():
    """Manage code snippets"""
    pass


@snippets.command(name="list")
def snippets_list():
    """List all available snippets"""
    console.print("[yellow]Command 'snippets list' not yet implemented[/yellow]")


@cli.command()
def status():
    """Show active sessions"""
    console.print("[yellow]Command 'status' not yet implemented[/yellow]")


@cli.command()
@click.argument("session_id", required=False)
def logs(session_id):
    """View session logs"""
    if session_id:
        console.print(f"[yellow]Logs for session {session_id} not yet implemented[/yellow]")
    else:
        console.print("[yellow]Command 'logs' requires a session ID[/yellow]")


@cli.command()
@click.option("--port", default=8000, help="Backend port (default: 8000)")
@click.option("--frontend-port", default=3001, help="Frontend port (default: 3001)")
def serve(port, frontend_port):
    """Start web dashboard with backend and frontend"""
    console.print("[yellow]Command 'serve' not yet implemented[/yellow]")


if __name__ == "__main__":
    cli()
