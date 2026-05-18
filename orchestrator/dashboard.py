"""Rich terminal dashboard for the multi-agent system."""
import threading
from datetime import datetime

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

console = Console()

_STATUS_COLORS = {
    "IDLE": "dim",
    "THINKING": "yellow",
    "WORKING": "green bold",
    "WAITING_FOR_USER": "cyan",
    "DONE": "bright_green",
    "ERROR": "red bold",
}

_LOG_COLORS = {
    "INFO": "white",
    "WARN": "yellow",
    "ERROR": "red",
    "SUCCESS": "bright_green",
}


class Dashboard:
    def __init__(self, project_name: str = "Unnamed Project", phase: str = "init"):
        self.project_name = project_name
        self.phase = phase
        self.active_task = "None"
        self.token_saving = True

        self.manager_messages: list[tuple[str, str, str]] = []  # (ts, role, msg)
        self.agent_statuses: dict[str, str] = {
            "planner": "IDLE",
            "backend": "IDLE",
            "frontend": "IDLE",
            "database": "IDLE",
            "tester": "IDLE",
            "reviewer": "IDLE",
            "git": "IDLE",
        }
        self.logs: list[tuple[str, str, str]] = []  # (ts, level, msg)

        self._lock = threading.Lock()
        self._live: Live | None = None

    # ── state mutators ────────────────────────────────────────────────────────

    def update_project(self, name: str = None, phase: str = None, task: str = None):
        with self._lock:
            if name is not None:
                self.project_name = name
            if phase is not None:
                self.phase = phase
            if task is not None:
                self.active_task = task

    def add_manager_message(self, message: str, role: str = "manager"):
        with self._lock:
            ts = datetime.now().strftime("%H:%M:%S")
            self.manager_messages.append((ts, role, message))
            if len(self.manager_messages) > 60:
                self.manager_messages = self.manager_messages[-60:]

    def set_agent_status(self, agent: str, status: str):
        with self._lock:
            if agent in self.agent_statuses:
                self.agent_statuses[agent] = status

    def add_log(self, message: str, level: str = "INFO"):
        with self._lock:
            ts = datetime.now().strftime("%H:%M:%S")
            self.logs.append((ts, level, message))
            if len(self.logs) > 120:
                self.logs = self.logs[-120:]

    # ── rendering ─────────────────────────────────────────────────────────────

    def _header_panel(self) -> Panel:
        mode = "[green]ON[/green]" if self.token_saving else "[red]OFF[/red]"
        text = (
            f"[bold cyan]PROJECT:[/bold cyan] [white]{self.project_name}[/white]   "
            f"[bold cyan]PHASE:[/bold cyan] [white]{self.phase.upper()}[/white]   "
            f"[bold cyan]ACTIVE TASK:[/bold cyan] [white]{self.active_task}[/white]   "
            f"[bold cyan]TOKEN-SAVE:[/bold cyan] {mode}"
        )
        return Panel(text, title="[bold blue]Multi-Agent Project Starter[/bold blue]", border_style="blue")

    def _manager_panel(self) -> Panel:
        with self._lock:
            msgs = list(self.manager_messages[-22:])
        lines = []
        for ts, role, msg in msgs:
            color = "bold magenta" if role == "manager" else "bold cyan"
            label = role.upper()
            # wrap long messages
            short_msg = msg[:200] + ("…" if len(msg) > 200 else "")
            lines.append(f"[dim]{ts}[/dim] [{color}]{label}[/{color}] {short_msg}")
        content = "\n".join(lines) if lines else "[dim]No messages yet…[/dim]"
        return Panel(content, title="[bold magenta]Manager Agent[/bold magenta]", border_style="magenta")

    def _agents_panel(self) -> Panel:
        with self._lock:
            statuses = dict(self.agent_statuses)
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold dim", padding=(0, 1))
        table.add_column("Agent", style="bold", width=12)
        table.add_column("Status", width=22)
        for agent, status in statuses.items():
            color = _STATUS_COLORS.get(status, "white")
            table.add_row(agent.capitalize(), f"[{color}]{status}[/{color}]")
        return Panel(table, title="[bold green]Worker Agents[/bold green]", border_style="green")

    def _logs_panel(self) -> Panel:
        with self._lock:
            recent = list(self.logs[-12:])
        lines = []
        for ts, level, msg in recent:
            color = _LOG_COLORS.get(level, "white")
            lines.append(f"[dim]{ts}[/dim] [{color}][{level}][/{color}] {msg}")
        content = "\n".join(lines) if lines else "[dim]No logs yet…[/dim]"
        return Panel(content, title="[bold]Logs / Next Actions[/bold]", border_style="dim")

    def make_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=14),
        )
        layout["main"].split_row(
            Layout(name="manager"),
            Layout(name="agents", size=36),
        )
        layout["header"].update(self._header_panel())
        layout["main"]["manager"].update(self._manager_panel())
        layout["main"]["agents"].update(self._agents_panel())
        layout["footer"].update(self._logs_panel())
        return layout

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def start(self):
        """Start the live dashboard. Returns self for use as context manager."""
        self._live = Live(
            self.make_layout(),
            refresh_per_second=2,
            screen=True,
            console=console,
        )
        self._live.start()
        return self

    def refresh(self):
        if self._live:
            self._live.update(self.make_layout())

    def pause(self):
        """Stop rendering so terminal input can be collected."""
        if self._live:
            self._live.stop()

    def resume(self):
        """Restart rendering after input."""
        if self._live:
            self._live.start()

    def stop(self):
        if self._live:
            self._live.stop()
            self._live = None

    def __enter__(self):
        return self.start()

    def __exit__(self, *_):
        self.stop()
