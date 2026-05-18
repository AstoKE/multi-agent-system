Review recent code changes using the Reviewer Agent.

Steps:
1. Ask the user: "Which files or areas should I review?" 
   - Accept a file path, a feature name, or "recent changes"
2. Load only the relevant files (be selective — read memory first)
3. Run the Reviewer Agent with the selected code
4. Present findings grouped by severity: HIGH → MEDIUM → LOW
5. For HIGH severity issues: ask the user how they want to proceed before suggesting fixes
6. For MEDIUM/LOW: list recommendations the user can act on later
7. Append review findings to project-memory/decisions.md
8. If issues were fixed, update project-memory/changelog.md

Focus areas:
- Security vulnerabilities (OWASP Top 10)
- Logic errors and edge cases
- Missing error handling
- Performance issues

Do NOT block for:
- Style or formatting preferences
- Minor variable naming
- Personal taste

The result should be APPROVED, NEEDS CHANGES, or BLOCKED — be clear about the verdict.
