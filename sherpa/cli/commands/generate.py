"""
SHERPA V1 - Generate Command
Create instruction files for interactive agents with injected knowledge
"""

import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def generate_command():
    """
    Generate instruction files for interactive agents
    Creates:
    - .cursor/rules/ directory with knowledge snippets
    - CLAUDE.md with injected snippets
    - copilot-instructions.md with injected snippets
    """
    try:
        console.print("\n[bold cyan]🏔️  SHERPA Generate - Creating Instruction Files[/bold cyan]\n")

        # Get current working directory
        cwd = Path.cwd()

        # Get snippets from sherpa/snippets directory
        sherpa_root = Path(__file__).parent.parent.parent
        snippets_dir = sherpa_root / "snippets"

        # Load all snippet files
        snippets = load_snippets(snippets_dir)

        if not snippets:
            console.print("[yellow]⚠️  No snippets found. Using default configuration.[/yellow]\n")

        # Create .cursor/rules/ directory
        cursor_rules_dir = cwd / ".cursor" / "rules"
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Created directory: {cursor_rules_dir.relative_to(cwd)}")

        # Generate .cursor/rules/00-sherpa-knowledge.md
        cursor_rules_file = cursor_rules_dir / "00-sherpa-knowledge.md"
        generate_cursor_rules(cursor_rules_file, snippets)
        console.print(f"[green]✓[/green] Created file: {cursor_rules_file.relative_to(cwd)}")

        # Generate CLAUDE.md
        claude_file = cwd / "CLAUDE.md"
        generate_claude_md(claude_file, snippets)
        console.print(f"[green]✓[/green] Created file: {claude_file.relative_to(cwd)}")

        # Generate copilot-instructions.md
        copilot_file = cwd / "copilot-instructions.md"
        generate_copilot_instructions(copilot_file, snippets)
        console.print(f"[green]✓[/green] Created file: {copilot_file.relative_to(cwd)}")

        # Display summary
        console.print()
        summary_table = Table(title="Generated Files Summary", show_header=True)
        summary_table.add_column("File", style="cyan")
        summary_table.add_column("Snippets", style="green")
        summary_table.add_column("Size", style="yellow")

        summary_table.add_row(
            str(cursor_rules_file.relative_to(cwd)),
            str(len(snippets)),
            f"{cursor_rules_file.stat().st_size:,} bytes"
        )
        summary_table.add_row(
            str(claude_file.relative_to(cwd)),
            str(len(snippets)),
            f"{claude_file.stat().st_size:,} bytes"
        )
        summary_table.add_row(
            str(copilot_file.relative_to(cwd)),
            str(len(snippets)),
            f"{copilot_file.stat().st_size:,} bytes"
        )

        console.print(summary_table)
        console.print()

        # Success message
        success_panel = Panel(
            Text.from_markup(
                "[bold green]✓ Instruction files generated successfully![/bold green]\n\n"
                "[cyan]Next steps:[/cyan]\n"
                "1. Review generated files in your project\n"
                "2. Customize snippets in sherpa/snippets/ directory\n"
                "3. Use 'sherpa generate' again to regenerate files\n"
                "4. Start coding with enhanced AI assistance!"
            ),
            title="[bold green]Success[/bold green]",
            border_style="green"
        )
        console.print(success_panel)

    except Exception as e:
        console.print(f"[red]✗ Error generating files: {str(e)}[/red]")
        raise


def load_snippets(snippets_dir: Path) -> list:
    """
    Load all snippet files from the snippets directory
    Returns list of dicts with snippet metadata and content
    """
    snippets = []

    if not snippets_dir.exists():
        return snippets

    # Find all .md files in snippets directory
    for snippet_file in snippets_dir.glob("*.md"):
        # Skip test files
        if snippet_file.name.startswith("test-") or snippet_file.name.startswith("snippet-"):
            continue

        try:
            content = snippet_file.read_text()

            # Extract metadata from content
            title = snippet_file.stem.replace("-", " ").title()
            category = extract_category(content)

            snippets.append({
                "name": snippet_file.stem,
                "title": title,
                "category": category,
                "content": content,
                "file": snippet_file.name
            })
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not load {snippet_file.name}: {str(e)}[/yellow]")

    return snippets


def extract_category(content: str) -> str:
    """Extract category from snippet content"""
    for line in content.split("\n"):
        if line.startswith("## Category:"):
            return line.replace("## Category:", "").strip()
    return "general"


def generate_cursor_rules(file_path: Path, snippets: list):
    """Generate .cursor/rules/00-sherpa-knowledge.md file"""
    content = """# SHERPA Knowledge Base

This file contains organizational knowledge and best practices injected by SHERPA.
Use these patterns and snippets as reference when coding.

"""

    if snippets:
        content += "## Available Knowledge Snippets\n\n"
        for snippet in snippets:
            content += f"### {snippet['title']}\n\n"
            content += f"**Category:** {snippet['category']}\n\n"
            content += snippet['content'] + "\n\n"
            content += "---\n\n"
    else:
        content += """## Default Configuration

No custom snippets found. Add snippets to `sherpa/snippets/` directory.

### Example Snippet Structure

Create `.md` files in `sherpa/snippets/` with this format:

```markdown
# Snippet Title

## Category: category/subcategory
## Language: python, javascript
## Tags: tag1, tag2, tag3

## Description

Your snippet content here...
```
"""

    file_path.write_text(content)


def generate_claude_md(file_path: Path, snippets: list):
    """Generate CLAUDE.md file with injected knowledge"""
    content = """# Claude Development Instructions

This file contains development guidelines and organizational knowledge for Claude Code.

## Project Context

This project uses SHERPA to enhance development with organizational knowledge.

## Knowledge Base

"""

    if snippets:
        content += "The following knowledge snippets are available for reference:\n\n"
        for snippet in snippets:
            content += f"### {snippet['title']}\n\n"
            content += snippet['content'] + "\n\n"
    else:
        content += """No custom snippets loaded. Add snippets to `sherpa/snippets/` directory.

Run `sherpa generate` to regenerate this file after adding snippets.
"""

    content += """
## Development Guidelines

- Follow the patterns and best practices outlined in the knowledge snippets above
- Use organizational standards for code structure and naming conventions
- Refer to snippet examples when implementing similar functionality
- Keep code consistent with existing patterns

---

*Generated by SHERPA V1 - Autonomous Coding Orchestrator*
"""

    file_path.write_text(content)


def generate_copilot_instructions(file_path: Path, snippets: list):
    """Generate copilot-instructions.md file"""
    content = """# GitHub Copilot Instructions

This file provides context and instructions for GitHub Copilot.

## Project Guidelines

This project uses SHERPA for knowledge management and follows organizational best practices.

## Code Patterns

"""

    if snippets:
        content += "Please follow these organizational patterns when suggesting code:\n\n"
        for snippet in snippets:
            content += f"### {snippet['title']}\n\n"
            content += f"Category: {snippet['category']}\n\n"
            # Include first 500 characters of each snippet as context
            snippet_preview = snippet['content'][:500]
            if len(snippet['content']) > 500:
                snippet_preview += "...\n\n[See full snippet in .cursor/rules/00-sherpa-knowledge.md]"
            content += snippet_preview + "\n\n"
    else:
        content += """No custom patterns loaded. Add snippets to `sherpa/snippets/` directory.

Run `sherpa generate` to regenerate this file.
"""

    content += """
## Instructions

- Follow organizational coding standards
- Use patterns from the knowledge base above
- Maintain consistency with existing code
- Prioritize security and best practices

---

*Generated by SHERPA V1*
"""

    file_path.write_text(content)
