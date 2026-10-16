# MCP Server (Person B)

Owns: custom MCP server exposing data operations as tools to the agents.

## Before you write code

Fill in section 5 of [`../docs/architecture.md`](../docs/architecture.md) with the team — decide what tools you actually need before building them.

## Suggested starting tool set

| Tool | Purpose | Notes |
|---|---|---|
| `query_dataset` | Run a filter/select against the cleaned data | Keep the query language simple and constrained (don't hand the model raw SQL/eval unless you've thought through the risk) |
| `get_column_summary` | Return stats (mean, nulls, dtype, distinct count) for a column | Cheap way for the analysis agent to explore data without dumping it all into context |
| `run_stat_test` | Run a named statistical test (e.g. correlation, t-test) on specified columns | Return structured results, not prose |
| `save_intermediate_result` | Persist findings/artifacts between agent calls | Useful for your context-management story with Person A |
| `verify_claim` | Given a claim + column/row reference, check it against source data | This is what makes the critic agent's job possible |

## Suggested structure (Python SDK)

```
mcp-server/
├── README.md
├── server.py          # MCP server entry point, tool registration
├── src/
│   ├── data_tools.py    # implementations for query/summary/stat tools
│   └── verify_tools.py  # implementation for verify_claim
└── requirements.txt
```

## What "done" looks like

- Server starts and correctly lists its tools when connected to
- Each tool has a clear name, description, and JSON schema for its parameters — write these as if a model with zero other context has to figure out when to use them
- Errors come back as usable tool results (e.g. "column 'revenu' not found, did you mean 'revenue'?") rather than raw stack traces
- Coordinate with Person A on transport (stdio vs. SSE/HTTP) early — this affects how the orchestrator connects

## Starter dependency

```bash
pip install mcp
```

See the [MCP Python SDK docs](https://github.com/modelcontextprotocol/python-sdk) for the server scaffold.
