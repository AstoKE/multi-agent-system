Run the Planner Agent to create or update the project architecture and task breakdown.

Steps:
1. Read project-memory/brief.md
2. Read project-memory/architecture.md (if it exists — don't rewrite from scratch if already has content)
3. Read project-memory/tasks.md (avoid duplicating existing tasks)
4. Run the Planner Agent with the brief as context
5. Save the updated plan to project-memory/architecture.md
6. Extract the task list and append new tasks to project-memory/tasks.md
7. Append a summary to project-memory/decisions.md
8. Append to project-memory/changelog.md

What a good plan includes:
- Architecture overview (components, responsibilities, tech choices)
- Phased task breakdown (Phase 1, 2, 3…)
- Dependencies between tasks
- Risks and open questions for the user

Keep the plan realistic and incremental.
Do not over-engineer — prefer simple, proven patterns.
Flag any decisions that require user input.
