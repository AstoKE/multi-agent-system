#!/usr/bin/env python3
"""Multi-Agent Project Starter — CLI entry point."""
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from agent_runner import run_agent, summarize_output
from dashboard import Dashboard, console
from memory import (
    append_changelog,
    append_decision,
    append_task,
    get_memory_summary,
    load_brief,
    load_memory,
    save_architecture,
    save_brief,
    save_tasks,
)
from report import generate_report

ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "config.yaml"


# ── config helpers ────────────────────────────────────────────────────────────


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def save_config(config: dict):
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def _banner(text: str):
    console.print(f"\n[bold blue]▶ {text}[/bold blue]")


def _ok(text: str):
    console.print(f"[bright_green]✓[/bright_green] {text}")


def _warn(text: str):
    console.print(f"[yellow]⚠[/yellow]  {text}")


def _err(text: str):
    console.print(f"[red]✗[/red]  {text}")


# ── commands ──────────────────────────────────────────────────────────────────


def cmd_init(_args):
    """Initialise a new project: collect info, populate project-memory."""
    _banner("Multi-Agent Project Starter — Init")

    project_name = input("Project name: ").strip()
    if not project_name:
        _err("Project name cannot be empty.")
        sys.exit(1)

    description = input("Short description: ").strip()
    tech_stack = input("Tech stack (e.g. FastAPI + React + PostgreSQL): ").strip()

    # Update config
    config = load_config()
    config["project"]["name"] = project_name
    config["project"]["phase"] = "planning"
    config["project"]["description"] = description
    save_config(config)

    # Fill brief template
    template_path = ROOT / "templates" / "project-brief-template.md"
    template = template_path.read_text() if template_path.exists() else "# Project Brief\n"
    brief = (
        template
        .replace("{{PROJECT_NAME}}", project_name)
        .replace("{{DESCRIPTION}}", description)
        .replace("{{TECH_STACK}}", tech_stack)
        .replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
    )
    save_brief(brief)
    append_changelog(f"Project '{project_name}' initialised.")

    _ok(f"Project '{project_name}' ready.")
    console.print("\nNext steps:")
    console.print("  [cyan]python orchestrator/main.py plan[/cyan]        — create architecture")
    console.print("  [cyan]python orchestrator/main.py start[/cyan]       — open dashboard & chat")
    console.print("  [cyan]python orchestrator/main.py build-feature[/cyan] — build a feature")


def cmd_start(_args):
    """Open the live dashboard and run an interactive Manager Agent session."""
    config = load_config()
    project_name = config["project"].get("name") or "Unnamed Project"
    phase = config["project"].get("phase", "init")

    session_data: dict = {
        "user_request": "",
        "manager_decisions": [],
        "active_agents": ["manager"],
        "tasks_completed": [],
        "files_changed": [],
        "tests_run": "None",
        "problems": [],
        "next_steps": [],
    }

    dash = Dashboard(project_name=project_name, phase=phase)
    dash.start()

    try:
        dash.add_log("Session started", "SUCCESS")
        dash.add_manager_message(
            "Hello! I'm the Manager Agent. What would you like to work on today?"
        )
        dash.refresh()

        dash.pause()
        console.print("\n[bold]Manager:[/bold] Hello! What would you like to work on today?")
        user_input = input("You > ").strip()
        dash.resume()

        if not user_input:
            dash.add_log("No input. Exiting.", "WARN")
            dash.refresh()
            input("\nPress Enter to close...")
            return

        session_data["user_request"] = user_input
        dash.add_manager_message(user_input, role="user")
        dash.update_project(task=user_input[:60])
        dash.add_log("Running Manager Agent…", "INFO")
        dash.set_agent_status("planner", "THINKING")
        dash.refresh()

        memory_summary = get_memory_summary()
        result = run_agent("manager", task=user_input, memory_summary=memory_summary)

        if result["success"]:
            output = result["output"]
            dash.add_manager_message(output)
            dash.add_log("Manager agent completed.", "SUCCESS")
            session_data["manager_decisions"].append(output[:300])
            append_decision(f"User: {user_input}\n\nManager:\n{output}")
            append_changelog(f"Manager session: {user_input[:100]}")
        else:
            dash.add_log(f"Manager error: {result['error']}", "ERROR")
            session_data["problems"].append(result["error"])

        dash.set_agent_status("planner", "IDLE")
        dash.refresh()

        report_path = generate_report(session_data)
        dash.add_log(f"Report saved → {report_path.name}", "SUCCESS")
        dash.refresh()

        dash.pause()
        input("\nPress Enter to close the dashboard…")

    finally:
        dash.stop()


def cmd_plan(args):
    """Run the Planner Agent to create or update architecture."""
    _banner("Planner Agent")

    memory_summary = get_memory_summary()
    brief = load_brief()

    task = (
        getattr(args, "task", None)
        or input("Planning task (Enter for full project plan): ").strip()
        or "Create a complete architecture and phased task breakdown from the project brief."
    )

    console.print("[dim]Running Planner Agent…[/dim]")
    result = run_agent("planner", task=task, memory_summary=memory_summary, context=brief)

    if result["success"]:
        output = result["output"]
        console.print("\n[bold]Planner Output:[/bold]")
        console.print(output)
        save_architecture(output)
        append_decision(f"Planner created plan:\n{output[:400]}")
        append_changelog("Planner ran — architecture.md updated.")
        _ok("Architecture saved → project-memory/architecture.md")
    else:
        _err(result["error"])
        sys.exit(1)


def cmd_build_feature(args):
    """Build a feature using selected worker agents."""
    _banner("Build Feature")

    memory_summary = get_memory_summary()
    feature = (
        getattr(args, "feature", None)
        or input("Describe the feature to build: ").strip()
    )
    if not feature:
        _err("Feature description required.")
        sys.exit(1)

    console.print("\nSelect agents to run (Enter = skip):")
    agents_to_run = []
    for agent in ["backend", "frontend", "database"]:
        choice = input(f"  Use {agent} agent? [y/N]: ").strip().lower()
        if choice == "y":
            agents_to_run.append(agent)

    if not agents_to_run:
        _warn("No agents selected.")
        return

    session_data: dict = {
        "user_request": feature,
        "manager_decisions": [],
        "active_agents": agents_to_run,
        "tasks_completed": [],
        "files_changed": [],
        "tests_run": "None",
        "problems": [],
        "next_steps": [f"Review output from: {', '.join(agents_to_run)}"],
    }

    for agent in agents_to_run:
        console.print(f"\n[dim]Running {agent} agent…[/dim]")
        result = run_agent(agent, task=feature, memory_summary=memory_summary)
        if result["success"]:
            output = summarize_output(result["output"])
            console.print(f"\n[bold]{agent.upper()} OUTPUT:[/bold]")
            console.print(output)
            append_task(f"{agent}: {feature[:80]}", "DONE")
            session_data["tasks_completed"].append(f"{agent}: {feature[:60]}")
            append_decision(f"{agent} agent output (excerpt):\n{output[:300]}")
            memory_summary = get_memory_summary()  # refresh for next agent
        else:
            _err(f"{agent}: {result['error']}")
            session_data["problems"].append(f"{agent} error: {result['error']}")

    append_changelog(f"Built feature: {feature[:100]}")
    report_path = generate_report(session_data)
    _ok(f"Report saved → {report_path.name}")


def cmd_review(args):
    """Run the Reviewer Agent on a file or scope."""
    _banner("Reviewer Agent")

    memory_summary = get_memory_summary()
    scope = (
        getattr(args, "scope", None)
        or input("What to review (file path or description): ").strip()
        or "recent changes"
    )

    console.print("[dim]Running Reviewer Agent…[/dim]")
    result = run_agent("reviewer", task=f"Review: {scope}", memory_summary=memory_summary)

    if result["success"]:
        console.print("\n[bold]Review Output:[/bold]")
        console.print(result["output"])
        append_decision(f"Review of '{scope}':\n{result['output'][:400]}")
        _ok("Review complete.")
    else:
        _err(result["error"])
        sys.exit(1)


def cmd_report(_args):
    """Generate a session report from current project memory."""
    _banner("Generate Report")

    mem = load_memory()
    session_data: dict = {
        "user_request": "Manual report generation",
        "manager_decisions": [mem["decisions"][-600:]] if mem["decisions"].strip() else [],
        "active_agents": [],
        "tasks_completed": [],
        "files_changed": [],
        "tests_run": "None",
        "problems": [],
        "next_steps": ["Review project-memory/tasks.md for pending items."],
    }

    report_path = generate_report(session_data)
    _ok(f"Report saved → {report_path}")


def cmd_commit(_args):
    """Run the Git Agent to analyse changes and suggest a commit message."""
    _banner("Git Agent")

    memory_summary = get_memory_summary()
    console.print("[dim]Running Git Agent…[/dim]")
    result = run_agent(
        "git",
        task="Analyse recent changes and provide a conventional commit message suggestion.",
        memory_summary=memory_summary,
    )

    if result["success"]:
        console.print("\n[bold]Git Agent Output:[/bold]")
        console.print(result["output"])
        append_decision(f"Git agent suggestion:\n{result['output'][:300]}")
        append_changelog(f"Commit reviewed by Git Agent.")
        _ok("Done. Review suggestions above before committing.")
    else:
        _err(result["error"])
        sys.exit(1)


# ── CLI wiring ────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python orchestrator/main.py",
        description="Multi-Agent Project Starter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Commands:\n"
            "  init            Initialise a new project\n"
            "  start           Open live dashboard + Manager Agent session\n"
            "  plan            Run the Planner Agent\n"
            "  build-feature   Build a feature with worker agents\n"
            "  review          Review code with the Reviewer Agent\n"
            "  report          Generate a session report\n"
            "  commit          Get commit message from the Git Agent\n"
        ),
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Initialise a new project")
    sub.add_parser("start", help="Start manager session with live dashboard")

    p_plan = sub.add_parser("plan", help="Run the Planner Agent")
    p_plan.add_argument("--task", help="Specific planning task")

    p_bf = sub.add_parser("build-feature", help="Build a feature")
    p_bf.add_argument("--feature", help="Feature description")

    p_rev = sub.add_parser("review", help="Review code")
    p_rev.add_argument("--scope", help="File path or description of what to review")

    sub.add_parser("report", help="Generate session report")
    sub.add_parser("commit", help="Get commit message suggestion")

    return parser


def main():
    os.chdir(ROOT)  # always run relative to project root
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "init": cmd_init,
        "start": cmd_start,
        "plan": cmd_plan,
        "build-feature": cmd_build_feature,
        "review": cmd_review,
        "report": cmd_report,
        "commit": cmd_commit,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
