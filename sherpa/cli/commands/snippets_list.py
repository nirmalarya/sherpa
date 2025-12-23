"""
SHERPA V1 - CLI Snippets List Command
List all available code snippets from all sources
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from sherpa.core.snippet_manager import get_snippet_manager
from sherpa.core.logging_config import get_logger

console = Console()
logger = get_logger("sherpa.cli.snippets_list")


def snippets_list_command(category: str = None, source: str = None) -> None:
    """
    List all available code snippets

    Args:
        category: Filter by category (optional)
        source: Filter by source (built-in, project, local, org) (optional)
    """
    try:
        # Show header
        console.print()
        console.print(Panel(
            "[bold cyan]📚 Available Code Snippets[/bold cyan]\n\n"
            "Showing snippets from all sources",
            title="SHERPA Snippets",
            border_style="cyan"
        ))
        console.print()

        # Get snippet manager and load snippets
        manager = get_snippet_manager()

        with console.status("[cyan]Loading snippets...", spinner="dots"):
            manager.load_snippets()

        snippets = manager.get_all_snippets()

        # Apply filters
        if category:
            snippets = [s for s in snippets if s.category == category]
            if not snippets:
                console.print(f"[yellow]⚠️  No snippets found for category: {category}[/yellow]")
                return

        if source:
            snippets = [s for s in snippets if s.source == source]
            if not snippets:
                console.print(f"[yellow]⚠️  No snippets found for source: {source}[/yellow]")
                return

        if not snippets:
            console.print("[yellow]⚠️  No snippets found[/yellow]")
            console.print("\n[dim]Add snippets to sherpa/snippets/ or sherpa/snippets.local/[/dim]")
            return

        # Display snippets in a table
        _display_snippets_table(snippets)

        # Display summary by source
        _display_source_summary(manager)

        # Display available categories
        _display_categories(manager)

    except Exception as e:
        logger.error(f"Error listing snippets: {e}", exc_info=True)
        console.print(f"[red]❌ Error: {e}[/red]")


def _display_snippets_table(snippets) -> None:
    """Display snippets in a Rich table"""
    table = Table(
        title="📋 Snippet List",
        show_header=True,
        header_style="bold cyan",
        border_style="blue"
    )

    table.add_column("Title", style="white", no_wrap=False, width=30)
    table.add_column("Category", style="yellow", width=15)
    table.add_column("Source", style="magenta", width=12)
    table.add_column("Language", style="green", width=12)
    table.add_column("Tags", style="dim", width=25)

    # Group by category for better organization
    snippets_sorted = sorted(snippets, key=lambda s: (s.category, s.title))

    for snippet in snippets_sorted:
        # Format source with color
        source_text = Text()
        if snippet.source == "built-in":
            source_text.append("built-in", style="blue")
        elif snippet.source == "project":
            source_text.append("project", style="green")
        elif snippet.source == "local":
            source_text.append("local", style="cyan")
        elif snippet.source == "org":
            source_text.append("org", style="magenta")
        else:
            source_text.append(snippet.source, style="white")

        # Format tags
        tags_str = ", ".join(snippet.tags) if snippet.tags else "-"

        # Add row
        table.add_row(
            snippet.title,
            snippet.category,
            source_text,
            snippet.language or "-",
            tags_str
        )

    console.print(table)
    console.print()


def _display_source_summary(manager) -> None:
    """Display summary of snippets by source"""
    sources = manager.get_sources()

    if not sources:
        return

    # Create source summary table
    summary_table = Table(
        title="📊 Snippets by Source",
        show_header=True,
        header_style="bold magenta",
        border_style="magenta",
        box=None
    )

    summary_table.add_column("Source", style="cyan", width=15)
    summary_table.add_column("Count", style="yellow", justify="right", width=10)
    summary_table.add_column("Location", style="dim", no_wrap=False)

    # Source locations
    locations = {
        "built-in": "sherpa/snippets/ (package)",
        "project": "./sherpa/snippets/ (project)",
        "local": "./sherpa/snippets.local/ (developer)",
        "org": "S3 + Bedrock (organization)"
    }

    for source, count in sorted(sources.items()):
        location = locations.get(source, "-")
        summary_table.add_row(source, str(count), location)

    console.print(summary_table)
    console.print()


def _display_categories(manager) -> None:
    """Display available categories"""
    categories = manager.get_categories()

    if not categories:
        return

    console.print(Panel(
        f"[bold cyan]Available Categories:[/bold cyan]\n\n"
        + ", ".join([f"[yellow]{cat}[/yellow]" for cat in categories]) + "\n\n"
        + "[dim]Filter by category: sherpa snippets list --category <name>[/dim]",
        title="💡 Tip",
        border_style="green"
    ))
    console.print()
