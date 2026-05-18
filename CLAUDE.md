# Multi-Agent Project Starter

This repository is a multi-agent software development assistant system. Claude coordinates specialised agents (Backend, Frontend, Database, Tester, Reviewer, Git) to build software projects.

---

## Safety Rules

### NEVER — without explicit user confirmation:

- Delete any file (`rm`, `unlink`, shell redirects that overwrite)
- Modify `.env`, `.env.local`, `.env.production`, or any secrets file
- Run destructive database commands: `DROP TABLE`, `TRUNCATE`, `DELETE FROM` without `WHERE`
- Expose secrets, API keys, tokens, or passwords in output or logs
- Push to GitHub or any remote (`git push`)
- Perform refactors that change more than 3 files at once
- Run `rm -rf` or any recursive delete
- Modify CI/CD pipelines (`.github/workflows/`, Dockerfile, etc.)
- Squash or rewrite published commits

### ALWAYS:

- Explain the plan before making large changes — ask if the user agrees
- Keep changes small and focused — one concern per turn
- Update `project-memory/` after significant work
- Generate a report in `reports/` after each session
- Ask for confirmation before any destructive operation
- Read `project-memory/` before reading source files (saves tokens)
- Only activate the agents needed for the current task

---

## Project Memory

All project context lives in `project-memory/`:

| File              | Purpose                                    |
|-------------------|--------------------------------------------|
| `brief.md`        | What we're building and why                |
| `decisions.md`    | Key decisions made and their rationale     |
| `tasks.md`        | Task list with status (TODO / DONE)        |
| `architecture.md` | Technical architecture and component plan  |
| `changelog.md`    | Chronological log of changes               |

**Always update these files after significant work.**
**Always read them before reading source files.**

---

## Agent System

Agents are defined as markdown prompt files in `.claude/agents/`.

| Agent     | File                         | Role                                     |
|-----------|------------------------------|------------------------------------------|
| manager   | `.claude/agents/manager.md`  | Coordinates all other agents             |
| planner   | `.claude/agents/planner.md`  | Architecture, roadmap, task breakdown    |
| backend   | `.claude/agents/backend.md`  | API, services, business logic            |
| frontend  | `.claude/agents/frontend.md` | UI, components, client state             |
| database  | `.claude/agents/database.md` | Schema, migrations, queries              |
| tester    | `.claude/agents/tester.md`   | Tests, coverage, failure analysis        |
| reviewer  | `.claude/agents/reviewer.md` | Code quality, security, edge cases       |
| git       | `.claude/agents/git.md`      | Diffs, commit messages, PR summaries     |

The Manager Agent is the only agent that talks directly with the user. All other agents receive tasks from the Manager and return output to it.

---

## Token-Saving Rules

1. Read `project-memory/` before reading any source file
2. Load only the files directly relevant to the current task
3. Only activate agents that are needed for the current task
4. Summarise long agent outputs (>500 words) before passing to the next agent
5. Keep task assignments short and specific
6. Update memory after each major decision so future turns need less context

---

## Slash Commands

| Command                   | Description                            |
|---------------------------|----------------------------------------|
| `/project-start`          | Start a new session with Manager Agent |
| `/project-plan`           | Create or update the project plan      |
| `/project-build-feature`  | Build a feature with worker agents     |
| `/project-review`         | Review code with the Reviewer Agent    |
| `/project-report`         | Generate a session report              |
| `/project-commit`         | Get a commit message from the Git Agent|

---

## CLI Commands

```bash
python orchestrator/main.py init            # Initialise project
python orchestrator/main.py start           # Live dashboard + Manager session
python orchestrator/main.py plan            # Run Planner Agent
python orchestrator/main.py build-feature   # Build a feature
python orchestrator/main.py review          # Review code
python orchestrator/main.py report          # Generate report
python orchestrator/main.py commit          # Get commit suggestion
```

---

## Reporting

After each session, a report is generated in `reports/YYYY-MM-DD-HHmmss-session-report.md`.
Reports include: user request, decisions made, agents used, tasks completed, problems found, next steps.
