Analyse recent changes and prepare a commit using the Git Agent.

Steps:
1. Check git status and the diff of staged/unstaged changes
2. Run the Git Agent with the diff and project-memory context
3. The Git Agent will:
   - Summarise what changed
   - Flag any files that should NOT be committed (.env, secrets, debug code)
   - Suggest a conventional commit message
4. If dangerous files are detected: WARN the user immediately and stop
5. Present the suggested commit message to the user for approval
6. If approved, the user runs the commit themselves (never auto-commit)
7. Append to project-memory/changelog.md

Safety rules (always enforce):
- NEVER auto-commit — present the suggestion, let the user decide
- NEVER suggest including .env, .env.local, or any secrets file
- NEVER suggest force-pushing to main or master
- Flag any binary files >500KB
- Flag debug statements (console.log, print, debugger, TODO)

Commit message must follow Conventional Commits:
  feat(scope): description
  fix(scope): description
  docs(scope): description
  refactor(scope): description
  test(scope): description
  chore(scope): description
