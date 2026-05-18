Build a specific feature using the appropriate worker agents.

Steps:
1. Read project-memory/brief.md and project-memory/architecture.md for context
2. Ask the user: "Which feature are we building?"
3. Determine which agents are needed based on the feature:
   - API or server logic → Backend Agent
   - UI or client-side → Frontend Agent
   - Schema or data changes → Database Agent
   - Tests for the feature → Tester Agent
   Only activate the agents that are truly needed.
4. For each agent, compose a short, specific task that includes:
   - What to build
   - Any constraints or existing patterns to follow
   - How it connects to other components
5. Run agents in logical order (Database → Backend → Frontend → Tester)
6. Summarise each agent's output before passing to the next agent (token saving)
7. Update project-memory/tasks.md — mark tasks as DONE
8. Append to project-memory/changelog.md
9. Summarise what was built and list any follow-up items

Token-saving rules:
- Pass each agent only the context it needs
- Summarise outputs >500 words before forwarding
- Don't reload the full repo — use memory summaries
