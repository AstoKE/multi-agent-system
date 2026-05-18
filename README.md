# Multi-Agent Project Starter

A local CLI-based multi-agent development system. Clone this template, initialise your project, and let a team of specialised AI agents help you build software — coordinated by a Manager Agent that talks with you directly.

---

## What is this?

This is a **GitHub template repository** that gives you a ready-made multi-agent workflow powered by Claude Code. Instead of one Claude session doing everything, work is split across specialised agents:

- **Manager** — talks with you, decides what to do, coordinates the team
- **Planner** — creates architecture and task breakdowns
- **Backend** — APIs, services, business logic
- **Frontend** — UI, components, client state
- **Database** — schemas, migrations, queries
- **Tester** — writes and runs tests
- **Reviewer** — code quality and security review
- **Git** — commit messages and PR summaries

The system maintains a `project-memory/` directory that persists context across sessions — so agents always know where the project stands without re-reading the entire codebase every time.

---

## Installation

### Prerequisites

- Python 3.11+
- [Claude Code](https://claude.ai/code) installed and authenticated (`claude` in PATH)

### Setup

```bash
# Clone or use as a GitHub template
git clone <this-repo> my-project
cd my-project

# Install Python dependencies
pip install -r requirements.txt
```

### Verify Claude Code is available

```bash
claude --version
```

---

## How to Configure Claude Code

Claude Code must be installed and logged in:

```bash
# Install (if not already)
npm install -g @anthropic-ai/claude-code

# Login
claude login
```

The orchestrator calls `claude -p "<prompt>"` as a subprocess. The `command` key in `orchestrator/config.yaml` controls the binary name (default: `claude`).

---

## Starting a New Project

### Step 1 — Initialise

```bash
python orchestrator/main.py init
```

You'll be prompted for:
- Project name
- Short description
- Tech stack

This populates `project-memory/brief.md` and `orchestrator/config.yaml`.

### Step 2 — Plan

```bash
python orchestrator/main.py plan
```

Runs the Planner Agent. Outputs architecture and tasks into `project-memory/`.

### Step 3 — Open a session

```bash
python orchestrator/main.py start
```

Opens the live dashboard and starts a Manager Agent session. Type your goal and the Manager coordinates the right agents.

---

## CLI Reference

```
python orchestrator/main.py <command> [options]

Commands:
  init                    Set up a new project
  start                   Open live dashboard + Manager Agent session
  plan [--task TEXT]      Run the Planner Agent
  build-feature           Build a feature with worker agents
    [--feature TEXT]
  review [--scope TEXT]   Review code with the Reviewer Agent
  report                  Generate a session report
  commit                  Get a commit message suggestion
```

---

## How the Dashboard Works

Run `python orchestrator/main.py start` to open the terminal dashboard.

```
┌─────────────────────────────────────────────────────────────────┐
│ PROJECT: MyApp  │  PHASE: BUILDING  │  TASK: Auth endpoint  │ ON │
├───────────────────────────────┬─────────────────────────────────┤
│ Manager Agent                 │ Worker Agents                   │
│                               │  Planner    IDLE                │
│ [10:42] MANAGER Hello! What   │  Backend    WORKING             │
│ would you like to work on?    │  Frontend   IDLE                │
│                               │  Database   DONE                │
│ [10:43] USER Add JWT auth      │  Tester     IDLE                │
│                               │  Reviewer   IDLE                │
│ [10:43] MANAGER I'll use the  │  Git        IDLE                │
│ Backend + Database agents...  │                                 │
├───────────────────────────────┴─────────────────────────────────┤
│ Logs / Next Actions                                             │
│ [10:43] [INFO]    Session started                               │
│ [10:43] [SUCCESS] Manager agent completed                       │
│ [10:44] [SUCCESS] Report saved → reports/2026-05-18-...md       │
└─────────────────────────────────────────────────────────────────┘
```

**Agent statuses:**
- `IDLE` — waiting
- `THINKING` — processing the task
- `WORKING` — writing code or output
- `WAITING_FOR_USER` — needs input before continuing
- `DONE` — task complete
- `ERROR` — something went wrong

---

## How Agents Work

Each agent is a markdown file in `.claude/agents/` that defines:
- The agent's role and responsibilities
- Output format
- Principles to follow
- Safety rules

When the orchestrator runs an agent, it:
1. Loads the agent's markdown prompt
2. Appends the project memory summary
3. Appends any task-specific context
4. Appends the task itself
5. Calls `claude -p "<assembled prompt>"`
6. Returns the output

The Manager Agent decides which worker agents to use and in what order. It reads memory first, then assigns focused tasks.

---

## How to Add a New Agent

1. Create `.claude/agents/my-agent.md` with this structure:
   ```markdown
   # My Agent Name

   You are the [Name] Agent. [One-sentence role description.]

   ## Your Responsibilities
   - ...

   ## Output Format
   ### Section
   [description]

   ## Principles
   - ...
   ```

2. Add it to `orchestrator/config.yaml`:
   ```yaml
   agents:
     my-agent:
       file: ".claude/agents/my-agent.md"
       enabled: true
   ```

3. Update `.claude/agents/manager.md` to list your new agent in the "Worker Agents Available" table.

4. Call it in the orchestrator:
   ```python
   from agent_runner import run_agent
   result = run_agent("my-agent", task="Do X", memory_summary=get_memory_summary())
   ```

---

## Token-Saving Rules

This system is designed to minimise token usage across sessions:

| Rule | Detail |
|------|--------|
| Read memory first | Always load `project-memory/` before source files |
| Selective file loading | Only read files relevant to the current task |
| Agent selectivity | Only activate agents needed for the current task |
| Output summarisation | Long outputs (>2000 chars) are truncated before being passed to the next agent |
| Short task prompts | Each agent receives a focused, minimal task — not the entire project context |
| Memory updates | After major decisions, memory is updated so future sessions need less context |

---

## Safety Rules

The system enforces these rules by default:

**NEVER without explicit user confirmation:**
- Delete files
- Modify `.env` or secrets files
- Run `DROP TABLE`, `TRUNCATE`, `DELETE FROM` without `WHERE`
- Push to GitHub or any remote
- Perform large refactors (>3 files)
- Expose secrets or credentials

**ALWAYS:**
- Explain the plan before making changes
- Keep changes small and focused
- Update `project-memory/` after significant work
- Generate a report after each session

---

## Project Structure

```
multi-agent-project-starter/
├── .claude/
│   ├── agents/          # Agent system prompts (markdown)
│   │   ├── manager.md
│   │   ├── planner.md
│   │   ├── backend.md
│   │   ├── frontend.md
│   │   ├── database.md
│   │   ├── tester.md
│   │   ├── reviewer.md
│   │   └── git.md
│   └── commands/        # Claude slash commands
│       ├── project-start.md
│       ├── project-plan.md
│       ├── project-build-feature.md
│       ├── project-review.md
│       ├── project-report.md
│       └── project-commit.md
├── orchestrator/
│   ├── main.py          # CLI entry point
│   ├── config.yaml      # Project configuration
│   ├── agent_runner.py  # Subprocess wrapper for claude -p
│   ├── dashboard.py     # Rich terminal dashboard
│   ├── memory.py        # Read/write project-memory files
│   └── report.py        # Session report generator
├── project-memory/      # Persistent project context
│   ├── brief.md
│   ├── decisions.md
│   ├── tasks.md
│   ├── architecture.md
│   └── changelog.md
├── reports/             # Auto-generated session reports
├── templates/           # Brief and task templates
├── CLAUDE.md            # Instructions for Claude Code
├── README.md            # This file
└── requirements.txt
```

---

## Example Workflow

```bash
# 1. Init
python orchestrator/main.py init
# → Project name: TaskFlow API
# → Description: REST API for task management
# → Tech stack: FastAPI + PostgreSQL

# 2. Plan
python orchestrator/main.py plan
# → Planner Agent creates architecture + task list

# 3. Build a feature
python orchestrator/main.py build-feature --feature "User registration endpoint"
# → Select: backend=y, database=y, frontend=n
# → Database Agent creates users table migration
# → Backend Agent implements POST /api/auth/register

# 4. Review the code
python orchestrator/main.py review --scope "src/api/auth.py"
# → Reviewer Agent checks security and edge cases

# 5. Get a commit message
python orchestrator/main.py commit
# → Git Agent suggests: feat(auth): add user registration endpoint

# 6. Generate session report
python orchestrator/main.py report
# → Saved to reports/2026-05-18-120000-session-report.md
```

Or use Claude Code slash commands inside a Claude Code session:
```
/project-start
/project-plan
/project-build-feature
/project-review
/project-commit
/project-report
```

---

## Next Improvements (v2 ideas)

- Web dashboard (FastAPI + React) with real-time agent status via WebSocket
- Persistent task queue with SQLite
- Token usage tracking per agent per session
- Auto-summarisation: when memory files exceed a size threshold, compress them
- GitHub Actions integration: run Tester + Reviewer on every PR automatically
- Support for custom agent chains (e.g. "always run Tester after Backend")
- Agent retry logic with exponential backoff
- Multi-project support (switch between projects via config)

---

## Contributing

This is a template — fork it, adapt it, and build your own workflows on top. If you create useful new agents or commands, consider sharing them.

---

*Powered by [Claude Code](https://claude.ai/code)*
