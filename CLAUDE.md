# bandwidth-game

- **Company:** Rigel
- **Local path:** `/Users/jmedina/developer/bandwidth-game`
- **Repo:** https://github.com/mrhobbes79/bandwidth-game.git

## How to work on this project

- Read `rigel/context.md` for the latest snapshot (branch, commit, next steps, blockers). RIGEL Workspace keeps it current.
- Archived sessions live under `rigel/sessions/`. Use them to reconstruct context after long gaps.
- Reusable prompts live under `rigel/prompts/`. Prefer pulling one in over freestyling when the situation fits.
- Ops runbooks live under `rigel/ops/`.

## Operational rules

- Plan before coding. For non-trivial work, propose an approach first.
- Run the project's build and tests before declaring a task done.
- Respect destructive-action boundaries: no force-push, no reset --hard, no branch delete without confirmation.
- If you discover a useful pattern or fix, consider writing a prompt into `rigel/prompts/`.

<!-- Managed collaboratively by the user and RIGEL Workspace.
     Initialization will not overwrite this file. Edit freely. -->

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
