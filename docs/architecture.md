# Architecture Decisions

Fill this in **together** in your first working session, before anyone writes code. Being able to justify these choices out loud is exactly what the CCA-F exam tests — treat this doc as your rehearsal.

## 1. Dataset

- **What data are we using?**
- **Why is it a good fit** (messy enough to need cleaning, rich enough to need real analysis)?
- **Where does it live?** (local `data/` folder, gitignored)

## 2. Orchestration pattern

- [x] **Supervisor/worker** (the orchestrator delegates to each worker agent in sequence and checks its output before proceeding — no separate critic agent)

**Why this pattern for this task?**
The orchestrator itself acts as the checkpoint between every stage (ingestion → analysis → report), rather than delegating verification to a fourth "critic" agent. This keeps the pipeline to three worker agents + one hub, and gives the orchestrator full visibility into every handoff, which simplifies the context-management story (see section 4).

**What are the failure modes of this pattern, and how do we mitigate them?**
- *Orchestrator becomes overloaded* (routing + judging is a lot of responsibility for one component) → mitigated by splitting its checking into two cheap layers: deterministic structural checks (fast, no API cost) run first, and an LLM-based judgment check only runs if those pass (see section 6).
- *Infinite retry loops* if an agent can't produce passing output → mitigated with `MAX_RETRIES_PER_STAGE` (see `orchestrator/config.py`); after that, the run halts and is flagged for human review instead of looping forever or silently proceeding with bad output.
- *Orchestrator's own LLM checks could be wrong too* → each checkpoint call is narrowly scoped (one specific handoff, not the whole pipeline state), which keeps its judgment focused; still worth tracking false-pass/false-fail rates once the eval set (`/eval`) is populated.

## 3. Agent responsibilities

| Agent | Input | Output | Tools it can call |
|---|---|---|---|
| Ingestion/cleaning | raw data | cleaned dataset + summary of changes made | MCP data tools |
| Analysis | cleaned dataset | structured findings (JSON) | MCP data tools |
| Report-writer | structured findings | draft report with citations to specific data points | — |
| Critic/verifier | draft report + underlying data | approved report OR list of flagged issues | MCP data tools (to re-check claims) |

## 4. Context management strategy

- **What gets passed between agents in full, vs. summarized/compacted?**
- **How does the critic agent get enough context to actually verify claims** without re-processing the entire dataset from scratch?
- **What's our strategy if the dataset is too large for a single context window?** (chunking, sampling, tool-based retrieval instead of dumping into context?)
- **What state persists across the whole run** (e.g. in files, via MCP tool results) vs. what's ephemeral per-agent-call?

## 5. Tool design (MCP)

- **What operations does the MCP server expose?** (e.g. `query_dataset`, `run_stat_test`, `get_column_summary`, `save_intermediate_result`)
- **Why these tools and not, say, giving the model direct code execution?** What's the trade-off?
- **How do tools report errors** back to the model in a way it can act on?

## 6. Verification / reliability

There is no separate critic agent — verification happens inline in the orchestrator at three checkpoints (after ingestion, after analysis, after report writing), each with two layers:

1. **Deterministic checks** (`orchestrator/checks/deterministic.py`) — structural validation: required keys present, correct types, non-empty, confidence values from an allowed set. No API call.
2. **LLM-based checks** (`orchestrator/checks/llm_checker.py`) — only runs if (1) passes. A narrowly-scoped Claude call judges whether the output is a faithful, well-supported result of its input (e.g. does a finding's `supporting_evidence` actually justify its claim). This is what catches fabricated or unsupported claims that pass structural validation.

**What happens when a check fails?** The orchestrator sends the failure reason back to the *same* agent as feedback and retries, up to `MAX_RETRIES_PER_STAGE` (default 3, see `orchestrator/config.py`). If still failing after that, the pipeline halts and flags that stage for human review (`PipelineState.needs_human_review`) rather than looping indefinitely or passing bad output downstream.

- **What's our eval set** for testing this? (see `/eval`) — TODO: extend `eval/test_cases.md` to test the orchestrator's checkpoints specifically (does it actually reject bad cleaning/analysis/report output, and does it approve good output rather than being over-strict).

> **Note for the team / Person C:** `prompts/critic_agent.md` was written for a separate critic agent that this design no longer uses. The verification logic is now the orchestrator's own prompts in `orchestrator/checks/llm_checker.py`. Worth a quick sync — that file can either be retired or repurposed as source material for tightening those checkpoint prompts.

## 7. Known trade-offs / open questions

Use this section honestly — the exam rewards being able to articulate *why* you chose X over Y, not pretending there's one right answer.
