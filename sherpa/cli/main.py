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
    from sherpa.cli.commands.run import run_command
    run_command(spec, source)


@cli.command()
@click.argument("query_text")
@click.option("--max-results", default=5, help="Maximum number of results to return")
def query(query_text, max_results):
    """Search Bedrock Knowledge Base for snippets"""
    from sherpa.cli.commands.query import query_command
    query_command(query_text, max_results)


@cli.group()
def snippets():
    """Manage code snippets"""
    pass


@snippets.command(name="list")
@click.option("--category", help="Filter by category")
@click.option("--source", help="Filter by source (built-in, project, local, org)")
def snippets_list(category, source):
    """List all available snippets"""
    from sherpa.cli.commands.snippets_list import snippets_list_command
    snippets_list_command(category, source)


@cli.command()
def status():
    """Show active sessions"""
    from sherpa.cli.commands.status import status_command
    status_command()


@cli.command()
@click.argument("session_id")
def logs(session_id):
    """View session logs"""
    from sherpa.cli.commands.logs import logs_command
    logs_command(session_id)


@cli.command()
@click.option("--port", default=8001, help="Backend port (default: 8001)")
@click.option("--frontend-port", default=3003, help="Frontend port (default: 3003)")
def serve(port, frontend_port):
    """Start web dashboard with backend and frontend"""
    from sherpa.cli.commands.serve import serve_command
    serve_command(port, frontend_port)


if __name__ == "__main__":
    cli()
