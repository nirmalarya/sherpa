"""
SHERPA V1 - CLI Query Command
Query AWS Bedrock Knowledge Base for code snippets
"""

import asyncio
from typing import List, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown

from sherpa.core.bedrock_client import get_bedrock_client
from sherpa.core.logging_config import get_logger

console = Console()
logger = get_logger("sherpa.cli.query")


def query_command(query_text: str, max_results: int = 5) -> None:
    """
    Query AWS Bedrock Knowledge Base for code snippets

    Args:
        query_text: The search query text
        max_results: Maximum number of results to return
    """
    try:
        # Show search header
        console.print()
        console.print(Panel(
            f"[bold cyan]🔍 Searching Knowledge Base[/bold cyan]\n\n"
            f"Query: [yellow]{query_text}[/yellow]\n"
            f"Max Results: [yellow]{max_results}[/yellow]",
            title="SHERPA Query",
            border_style="cyan"
        ))
        console.print()

        # Run async query
        results = asyncio.run(_execute_query(query_text, max_results))

        if not results:
            console.print("[yellow]⚠️  No results found[/yellow]")
            console.print("\n[dim]Try different search terms or check your Bedrock configuration[/dim]")
            return

        # Display results with Rich formatting
        _display_results(results, query_text)

    except Exception as e:
        logger.error(f"Error executing query: {e}", exc_info=True)
        console.print(f"[red]❌ Error: {e}[/red]")


async def _execute_query(query_text: str, max_results: int) -> List[Dict[str, Any]]:
    """
    Execute the query asynchronously

    Args:
        query_text: The search query text
        max_results: Maximum number of results

    Returns:
        List of search results
    """
    # Get Bedrock client
    bedrock_client = get_bedrock_client()

    # Connect to Bedrock
    connected = await bedrock_client.connect()
    if not connected:
        console.print("[red]❌ Failed to connect to Bedrock Knowledge Base[/red]")
        return []

    # Execute query
    with console.status(f"[cyan]Querying knowledge base...", spinner="dots"):
        results = await bedrock_client.query(
            query_text=query_text,
            max_results=max_results,
            min_score=0.5
        )

    return results


def _display_results(results: List[Dict[str, Any]], query_text: str) -> None:
    """
    Display search results with Rich formatting

    Args:
        results: List of search results
        query_text: Original query text
    """
    console.print(f"[bold green]✅ Found {len(results)} results[/bold green]\n")

    for i, result in enumerate(results, 1):
        score = result.get('score', 0)
        content = result.get('content', '')
        metadata = result.get('metadata', {})
        location = result.get('location', {})

        # Create result header table
        header_table = Table(show_header=False, box=None, padding=(0, 1))
        header_table.add_column("Field", style="cyan")
        header_table.add_column("Value")

        header_table.add_row("Relevance Score", f"[yellow]{score:.2f}[/yellow]")
        header_table.add_row("Source", location.get('source', 'Unknown'))
        header_table.add_row("Category", metadata.get('category', 'N/A'))

        tags = metadata.get('tags', [])
        if tags:
            header_table.add_row("Tags", ", ".join(f"[blue]{tag}[/blue]" for tag in tags))

        # Display result panel
        console.print(Panel(
            header_table,
            title=f"[bold white]Result {i}[/bold white]",
            border_style="green" if score >= 0.8 else "yellow"
        ))

        # Display content preview (first 1000 characters)
        preview_length = 1000
        if len(content) > preview_length:
            preview = content[:preview_length] + "\n\n[dim]... (truncated)[/dim]"
        else:
            preview = content

        # Try to render as markdown if it looks like markdown
        if content.strip().startswith('#') or '```' in content:
            try:
                console.print(Markdown(preview))
            except Exception:
                # Fallback to plain text if markdown rendering fails
                console.print(preview)
        else:
            console.print(preview)

        console.print()  # Add spacing between results

    # Summary footer
    console.print(Panel(
        f"[dim]Showing {len(results)} results for query: [cyan]{query_text}[/cyan][/dim]",
        border_style="dim"
    ))
