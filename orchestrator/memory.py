"""Manages project-memory files."""
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
MEMORY_DIR = ROOT / "project-memory"

_FILES = {
    "brief": "brief.md",
    "decisions": "decisions.md",
    "tasks": "tasks.md",
    "architecture": "architecture.md",
    "changelog": "changelog.md",
}


def _path(key: str) -> Path:
    return MEMORY_DIR / _FILES[key]


def load_memory() -> dict:
    """Load all project-memory files into a dict."""
    return {key: (_path(key).read_text() if _path(key).exists() else "") for key in _FILES}


def load_brief() -> str:
    return _path("brief").read_text() if _path("brief").exists() else ""


def save_brief(content: str):
    _path("brief").write_text(content)


def load_decisions() -> str:
    return _path("decisions").read_text() if _path("decisions").exists() else ""


def append_decision(decision: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    existing = _path("decisions").read_text() if _path("decisions").exists() else "# Decisions\n"
    _path("decisions").write_text(existing + f"\n## {ts}\n{decision.strip()}\n")


def load_tasks() -> str:
    return _path("tasks").read_text() if _path("tasks").exists() else ""


def save_tasks(content: str):
    _path("tasks").write_text(content)


def append_task(task: str, status: str = "TODO"):
    existing = _path("tasks").read_text() if _path("tasks").exists() else "# Tasks\n"
    _path("tasks").write_text(existing + f"- [{status}] {task}\n")


def load_architecture() -> str:
    return _path("architecture").read_text() if _path("architecture").exists() else ""


def save_architecture(content: str):
    _path("architecture").write_text(content)


def append_changelog(entry: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    existing = _path("changelog").read_text() if _path("changelog").exists() else "# Changelog\n"
    _path("changelog").write_text(existing + f"\n## {ts}\n{entry.strip()}\n")


def get_memory_summary() -> str:
    """Return a condensed memory snapshot for token-saving."""
    mem = load_memory()
    parts = []
    if mem["brief"].strip():
        parts.append(f"### Brief\n{mem['brief'][:600]}")
    if mem["tasks"].strip():
        parts.append(f"### Tasks\n{mem['tasks'][:400]}")
    if mem["decisions"].strip():
        parts.append(f"### Recent Decisions\n{mem['decisions'][-600:]}")
    if mem["architecture"].strip():
        parts.append(f"### Architecture (excerpt)\n{mem['architecture'][:400]}")
    return "\n\n".join(parts) if parts else "(no project memory yet)"
