Start a new Manager Agent session for this project.

Steps:
1. Read project-memory/brief.md — understand what we're building
2. Read project-memory/tasks.md — see what's pending
3. Read project-memory/decisions.md (last 500 chars) — context for recent decisions
4. Greet the user and ask what they want to accomplish in this session
5. If no brief exists yet, ask:
   - Project name
   - What are we building?
   - Tech stack preferences
   - What's the priority for today?
   Then write a brief to project-memory/brief.md
6. Based on the user's answer, decide which agents are needed
7. Assign tasks and coordinate
8. Summarise what was done and what's next
9. Append to project-memory/changelog.md

Token-saving reminder:
- Read memory BEFORE reading source files
- Only activate agents that are relevant to today's goal
- Summarise long agent outputs before passing to the next agent
