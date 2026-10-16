# Orchestrator (Person A)

Owns: agent loop, handoffs between agents, checkpoint verification, retry/escalation logic, context strategy.

## Design (see `docs/architecture.md` for full rationale)

The orchestrator acts as the **checker between every stage** — there's no separate critic agent. Flow:

```
raw data → ingestion agent → [checkpoint] → analysis agent → [checkpoint] → report agent → [checkpoint] → final report
```

Each `[checkpoint]`:
1. Runs a **deterministic check** (`checks/deterministic.py`) — cheap, structural, no API call.
2. If that passes, runs an **LLM-based judgment check** (`checks/llm_checker.py`) — catches things code can't (fabricated stats, unsupported claims, dropped caveats).
3. If either fails, the stage's agent is retried with feedback, up to `config.MAX_RETRIES_PER_STAGE` times.
4. If still failing, the run halts and is flagged for human review (`PipelineState.needs_human_review`).

## Structure

```
orchestrator/
├── main.py                  # entry point — runs the full pipeline
├── config.py                 # models, retry limits, feature flags
├── state.py                  # PipelineState — tracks outputs + checkpoint history
├── utils.py                  # prompt loading, JSON response parsing
├── data_utils.py              # Phase 1: text data preview (no MCP needed yet)
├── checks/
│   ├── deterministic.py        # structural validation per stage
│   └── llm_checker.py           # LLM-based judgment checks per stage
└── agents/
    ├── base_agent.py            # shared Claude call + tool-use loop wrapper
    ├── ingestion_agent.py
    ├── analysis_agent.py
    └── report_agent.py
```

## Running it (Phase 1 — no MCP needed)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
python -m orchestrator.main --data path/to/your_dataset.csv
```

This runs the whole pipeline using text-based data previews (`data_utils.quick_data_preview`) instead of MCP tool calls, so you can test orchestration/checkpoint logic without waiting on Person B's MCP server.

## Phase 2 TODO (once mcp-server/ is ready)

Swap each worker agent from using `quick_data_preview` text to using real MCP tools:
- In `agents/*.py`, pass `tools=[...]` (the MCP tool schemas) to `BaseAgent`
- Pass a `tool_executor` callable to `.run()` that dispatches `tool_use` blocks to Person B's MCP server
- Coordinate transport (stdio vs SSE/HTTP) with Person B

## Coordinate with Person C

The prompt files this orchestrator loads (`prompts/ingestion_agent.md`, `prompts/analysis_agent.md`, `prompts/report_writer.md`) are owned by Person C — if you need output schema changes, that's a shared conversation, not just an orchestrator change (deterministic checks in `checks/deterministic.py` assume specific keys).

`prompts/critic_agent.md` is no longer used by a standalone agent — see the note in `docs/architecture.md` section 6.
