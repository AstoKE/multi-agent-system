Generate a session report summarising work done.

Steps:
1. Read project-memory/decisions.md (last 1000 chars for recent decisions)
2. Read project-memory/tasks.md (completed and pending tasks)
3. Read project-memory/changelog.md (last 500 chars for recent changes)
4. Compose a structured report including:
   - Session summary (what was worked on)
   - Key decisions made
   - Tasks completed
   - Tasks still pending
   - Problems or blockers found
   - Recommended next steps (prioritised)
5. Save the report to reports/YYYY-MM-DD-HHmm-session-report.md
6. Print the report path and a brief summary to the user

Report format:
```
# Session Report — YYYY-MM-DD HH:MM

## Summary
[2-3 sentences]

## Decisions Made
- ...

## Tasks Completed
- ...

## Pending Tasks
- ...

## Problems Found
- ...

## Next Steps
1. ...
```

Keep it concise and actionable — the goal is a useful handoff document for the next session.
