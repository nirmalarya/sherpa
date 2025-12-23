"""
SHERPA V1 - CLI Serve Command
Start web dashboard with backend FastAPI and frontend Vite dev server
"""

import subprocess
import time
import signal
import sys
import os
from pathlib import Path
from typing import Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text

from sherpa.core.logging_config import get_logger
import httpx

console = Console()
logger = get_logger("sherpa.cli.serve")


class ServerProcess:
    """Manage a server process with health checking"""

    def __init__(self, name: str, command: List[str], cwd: Optional[Path] = None, health_url: Optional[str] = None):
        self.name = name
        self.command = command
        self.cwd = cwd
        self.health_url = health_url
        self.process: Optional[subprocess.Popen] = None
        self.healthy = False

    def start(self) -> bool:
        """Start the server process"""
        try:
            logger.info(f"Starting {self.name}...")
            self.process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            logger.info(f"{self.name} started with PID {self.process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start {self.name}: {e}")
            return False

    def check_health(self, timeout: int = 30) -> bool:
        """Check if server is healthy"""
        if not self.health_url:
            # No health check URL, assume healthy if process is running
            return self.process is not None and self.process.poll() is None

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.process and self.process.poll() is not None:
                # Process died
                return False

            try:
                response = httpx.get(self.health_url, timeout=1.0)
                if response.status_code == 200:
                    self.healthy = True
                    return True
            except (httpx.ConnectError, httpx.TimeoutException):
                pass

            time.sleep(0.5)

        return False

    def stop(self):
        """Stop the server process"""
        if self.process:
            try:
                logger.info(f"Stopping {self.name}...")
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"{self.name} did not terminate, killing...")
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None
                self.healthy = False


def create_status_table(backend_server: ServerProcess, frontend_server: ServerProcess) -> Table:
    """Create a table showing server status"""
    table = Table(show_header=True, header_style="bold cyan", border_style="cyan")
    table.add_column("Service", style="cyan", width=15)
    table.add_column("Status", width=12)
    table.add_column("URL", style="blue underline", width=30)

    # Backend status
    backend_status = "✅ Running" if backend_server.healthy else "⏳ Starting..."
    table.add_row(
        "Backend API",
        backend_status,
        backend_server.health_url or "N/A"
    )

    # Frontend status
    frontend_status = "✅ Running" if frontend_server.healthy else "⏳ Starting..."
    frontend_url = frontend_server.health_url or "N/A"
    table.add_row(
        "Frontend",
        frontend_status,
        frontend_url
    )

    return table


def serve_command(port: int = 8001, frontend_port: int = 3003) -> None:
    """
    Start web dashboard with backend and frontend servers

    Args:
        port: Backend API port (default: 8001)
        frontend_port: Frontend dev server port (default: 3003)
    """
    backend_server: Optional[ServerProcess] = None
    frontend_server: Optional[ServerProcess] = None

    def signal_handler(sig, frame):
        """Handle Ctrl+C gracefully"""
        console.print("\n[yellow]Shutting down servers...[/yellow]")
        if backend_server:
            backend_server.stop()
        if frontend_server:
            frontend_server.stop()
        console.print("[green]Servers stopped successfully[/green]")
        sys.exit(0)

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Show header
        console.print()
        console.print(Panel(
            "[bold cyan]🚀 Starting SHERPA Dashboard[/bold cyan]\n\n"
            "[dim]Starting backend API and frontend dev server...[/dim]",
            title="SHERPA Serve",
            border_style="cyan"
        ))
        console.print()

        # Get project root (where sherpa/ directory is)
        project_root = Path(__file__).parent.parent.parent.parent
        frontend_dir = project_root / "sherpa" / "frontend"

        # Check if frontend directory exists
        if not frontend_dir.exists():
            console.print(f"[red]❌ Frontend directory not found: {frontend_dir}[/red]")
            console.print("[yellow]Expected frontend at: sherpa/frontend/[/yellow]")
            return

        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            console.print("[yellow]⚠️  Frontend dependencies not installed[/yellow]")
            console.print(f"[dim]Run: cd {frontend_dir} && npm install[/dim]")
            return

        # Create backend server
        backend_server = ServerProcess(
            name="Backend API",
            command=[
                "python", "-m", "uvicorn",
                "sherpa.api.main:app",
                "--reload",
                "--port", str(port),
                "--host", "0.0.0.0"
            ],
            cwd=project_root,
            health_url=f"http://localhost:{port}/health"
        )

        # Create frontend server
        frontend_server = ServerProcess(
            name="Frontend",
            command=[
                "npm", "run", "dev"
            ],
            cwd=frontend_dir,
            health_url=f"http://localhost:{frontend_port}"
        )

        # Start backend
        console.print("[cyan]Starting backend API...[/cyan]")
        if not backend_server.start():
            console.print("[red]❌ Failed to start backend API[/red]")
            return

        # Start frontend
        console.print("[cyan]Starting frontend dev server...[/cyan]")
        if not frontend_server.start():
            console.print("[red]❌ Failed to start frontend[/red]")
            backend_server.stop()
            return

        # Wait for servers to be healthy
        console.print()
        console.print("[yellow]Waiting for servers to be ready...[/yellow]")

        with Live(create_status_table(backend_server, frontend_server), refresh_per_second=2) as live:
            # Check backend health
            backend_ready = backend_server.check_health(timeout=30)
            live.update(create_status_table(backend_server, frontend_server))

            if not backend_ready:
                console.print("\n[red]❌ Backend API failed to start[/red]")
                backend_server.stop()
                frontend_server.stop()
                return

            # Check frontend health
            frontend_ready = frontend_server.check_health(timeout=30)
            live.update(create_status_table(backend_server, frontend_server))

            if not frontend_ready:
                console.print("\n[red]❌ Frontend failed to start[/red]")
                backend_server.stop()
                frontend_server.stop()
                return

        # Success!
        console.print()
        console.print(Panel(
            "[bold green]✅ SHERPA Dashboard is running![/bold green]\n\n"
            f"[cyan]Backend API:[/cyan] http://localhost:{port}\n"
            f"[cyan]API Docs:[/cyan] http://localhost:{port}/docs\n"
            f"[cyan]Frontend:[/cyan] http://localhost:{frontend_port}\n\n"
            "[yellow]Press Ctrl+C to stop servers[/yellow]",
            title="🎉 Success",
            border_style="green"
        ))

        # Keep running
        console.print()
        console.print("[dim]Servers are running. Logs will appear below:[/dim]")
        console.print()

        # Wait forever (until Ctrl+C)
        while True:
            time.sleep(1)

            # Check if processes are still alive
            if backend_server.process and backend_server.process.poll() is not None:
                console.print("[red]❌ Backend API crashed[/red]")
                break

            if frontend_server.process and frontend_server.process.poll() is not None:
                console.print("[red]❌ Frontend crashed[/red]")
                break

    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down servers...[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        logger.error(f"Serve command error: {e}", exc_info=True)
    finally:
        # Cleanup
        if backend_server:
            backend_server.stop()
        if frontend_server:
            frontend_server.stop()
        console.print("[green]✅ Servers stopped[/green]")
