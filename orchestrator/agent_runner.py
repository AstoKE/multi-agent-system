"""Runs Claude agents via subprocess using claude -p."""
import subprocess
from pathlib import Path
import yaml

ROOT = Path(__file__).parent.parent
AGENTS_DIR = ROOT / ".claude" / "agents"


def load_config() -> dict:
    with open(Path(__file__).parent / "config.yaml") as f:
        return yaml.safe_load(f)


def load_agent_prompt(agent_name: str) -> str:
    prompt_file = AGENTS_DIR / f"{agent_name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Agent prompt not found: {prompt_file}")
    return prompt_file.read_text()


def build_prompt(agent_name: str, task: str, context: str = "", memory_summary: str = "") -> str:
    parts = [load_agent_prompt(agent_name)]
    if memory_summary and memory_summary.strip() != "(no project memory yet)":
        parts.append(f"## Project Memory\n{memory_summary}")
    if context:
        parts.append(f"## Context\n{context}")
    parts.append(f"## Your Task\n{task}")
    return "\n\n---\n\n".join(parts)


def run_agent(
    agent_name: str,
    task: str,
    context: str = "",
    memory_summary: str = "",
    timeout: int = 300,
) -> dict:
    """Run a named agent and return a result dict."""
    config = load_config()
    claude_cmd = config.get("claude", {}).get("command", "claude")
    effective_timeout = config.get("claude", {}).get("timeout", timeout)

    prompt = build_prompt(agent_name, task, context, memory_summary)

    try:
        result = subprocess.run(
            [claude_cmd, "-p", prompt],
            capture_output=True,
            text=True,
            timeout=effective_timeout,
            cwd=str(ROOT),
        )
        success = result.returncode == 0
        return {
            "agent": agent_name,
            "success": success,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if not success else "",
            "task": task,
        }
    except subprocess.TimeoutExpired:
        return {
            "agent": agent_name,
            "success": False,
            "output": "",
            "error": f"Agent '{agent_name}' timed out after {effective_timeout}s",
            "task": task,
        }
    except FileNotFoundError:
        return {
            "agent": agent_name,
            "success": False,
            "output": "",
            "error": (
                f"Claude CLI not found. Install Claude Code and ensure "
                f"'{claude_cmd}' is in your PATH."
            ),
            "task": task,
        }


def summarize_output(output: str, max_chars: int = 2000) -> str:
    """Truncate long outputs for token saving."""
    if len(output) <= max_chars:
        return output
    half = max_chars // 2
    return (
        output[:half]
        + "\n\n[... truncated for token saving ...]\n\n"
        + output[-half:]
    )
