# Claude Code Workspace (Person C)

Owns: dev environment setup, custom slash commands, and (with prompts/) the system prompts for each agent.

## Suggested structure

```
claude-code/
├── README.md
├── .claude/
│   ├── commands/
│   │   ├── run-pipeline.md     # slash command to run the full pipeline
│   │   └── run-eval.md         # slash command to run the eval set
│   └── settings.json           # project-level Claude Code settings (checked in)
```

`settings.local.json` (personal, gitignored) is where each person can put their own local overrides.

## What "done" looks like

- `.claude/commands/` has at least one working custom slash command relevant to this project (e.g. `/run-pipeline`)
- Team members can clone the repo and get a working Claude Code setup with minimal manual steps
- You can explain *why* you structured the commands/config the way you did — that's the part the exam actually tests, not just that it works

## Coordinate with

- **Person A** on how the orchestrator gets invoked (so your slash command actually calls the right entry point)
- **Person B** on the MCP server connection so Claude Code (if used interactively) can also reach the tools directly for debugging
