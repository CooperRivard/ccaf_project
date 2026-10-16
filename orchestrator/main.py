"""
Orchestrator entry point.

Flow: raw data -> ingestion agent -> [checkpoint] -> analysis agent ->
[checkpoint] -> report agent -> [checkpoint] -> final report.

Each checkpoint runs deterministic checks first, then (if those pass) an
LLM-based judgment check. If a stage fails a checkpoint, the orchestrator
sends it back to the SAME agent with feedback describing what failed, up to
config.MAX_RETRIES_PER_STAGE times. If it still fails after that, the run
halts and is flagged for human review rather than silently proceeding with
bad output or looping forever.

Usage:
    python -m orchestrator.main --data path/to/dataset.csv
    python -m orchestrator.main --data path/to/dataset.csv --verbose
    python -m orchestrator.main --data path/to/dataset.csv --debug-out run_debug.json
"""
import argparse
import json
import sys
import time

from dotenv import load_dotenv

load_dotenv()  # reads .env from the current working directory (repo root) if present

from . import config
from .agents.analysis_agent import run_analysis_agent
from .agents.ingestion_agent import run_ingestion_agent
from .agents.report_agent import run_report_agent
from .checks import deterministic, llm_checker
from .data_utils import quick_data_preview
from .state import CheckpointResult, PipelineState

VERBOSE = False


def log(msg: str) -> None:
    """Progress logging, only shown with --verbose. Always flushes immediately
    so output appears live rather than buffering while an API call is in flight."""
    if VERBOSE:
        print(f"  ... {msg}", flush=True)


def print_failure_detail(stage: str, attempt: int, raw_output, result: CheckpointResult) -> None:
    """Always printed (not gated by --verbose) — this is the answer to
    'what actually happened' when a stage fails a checkpoint."""
    print(f"\n--- [{stage}] attempt {attempt} FAILED ---")
    if not result.deterministic_passed:
        print(f"Deterministic check reason: {result.deterministic_reason}")
    else:
        print(f"LLM check reason: {result.llm_reason}")
    print("Raw agent output for this attempt:")
    print(json.dumps(raw_output, indent=2) if isinstance(raw_output, dict) else raw_output)
    print("---\n")


def run_checkpoint(
    state: PipelineState,
    stage: str,
    attempt: int,
    raw_output,
    det_result,
    llm_result_fn,
) -> CheckpointResult:
    log(f"[{stage}] attempt {attempt}: running deterministic check...")
    llm_passed = None
    llm_reason = None

    if det_result.passed and config.ENABLE_LLM_CHECKS:
        log(f"[{stage}] attempt {attempt}: deterministic PASS, running LLM check...")
        llm_result = llm_result_fn()
        llm_passed = llm_result.passed
        llm_reason = llm_result.reason
    elif not det_result.passed:
        log(f"[{stage}] attempt {attempt}: deterministic FAIL, skipping LLM check")

    result = CheckpointResult(
        stage=stage,
        attempt=attempt,
        deterministic_passed=det_result.passed,
        deterministic_reason=det_result.reason,
        llm_passed=llm_passed,
        llm_reason=llm_reason,
        raw_output=raw_output,
    )
    state.record_checkpoint(result)

    if result.passed:
        log(f"[{stage}] attempt {attempt}: PASS")
    else:
        print_failure_detail(stage, attempt, raw_output, result)

    return result


def failure_feedback(result: CheckpointResult) -> str:
    if not result.deterministic_passed:
        return f"Structural check failed: {result.deterministic_reason}"
    return f"Quality check failed: {result.llm_reason}"


def run_pipeline(data_path: str) -> PipelineState:
    state = PipelineState(raw_data_path=data_path)

    log(f"Loading data preview from {data_path}...")
    data_preview = quick_data_preview(data_path)
    log("Data preview loaded.")

    # ---- Stage 1: Ingestion / cleaning ----
    feedback = None
    print("Running ingestion agent...", flush=True)
    for attempt in range(1, config.MAX_RETRIES_PER_STAGE + 1):
        log(f"[ingestion] attempt {attempt}: calling agent...")
        t0 = time.time()
        cleaning_output = run_ingestion_agent(data_preview, feedback=feedback)
        log(f"[ingestion] attempt {attempt}: agent responded in {time.time()-t0:.1f}s")

        det = deterministic.check_cleaning_output(cleaning_output)
        result = run_checkpoint(
            state, "ingestion", attempt, cleaning_output, det,
            lambda: llm_checker.check_cleaning(data_preview, cleaning_output),
        )
        if result.passed:
            state.cleaning_output = cleaning_output
            break
        feedback = failure_feedback(result)
    else:
        state.needs_human_review = True
        state.human_review_stage = "ingestion"
        state.human_review_reason = feedback
        return state

    # ---- Stage 2: Analysis ----
    feedback = None
    print("Running analysis agent...", flush=True)
    for attempt in range(1, config.MAX_RETRIES_PER_STAGE + 1):
        log(f"[analysis] attempt {attempt}: calling agent...")
        t0 = time.time()
        analysis_output = run_analysis_agent(
            data_preview, state.cleaning_output, feedback=feedback
        )
        log(f"[analysis] attempt {attempt}: agent responded in {time.time()-t0:.1f}s")

        det = deterministic.check_analysis_output(analysis_output)
        result = run_checkpoint(
            state, "analysis", attempt, analysis_output, det,
            lambda: llm_checker.check_analysis(data_preview, analysis_output),
        )
        if result.passed:
            state.analysis_output = analysis_output
            break
        feedback = failure_feedback(result)
    else:
        state.needs_human_review = True
        state.human_review_stage = "analysis"
        state.human_review_reason = feedback
        return state

    # ---- Stage 3: Report writing ----
    feedback = None
    print("Running report-writer agent...", flush=True)
    for attempt in range(1, config.MAX_RETRIES_PER_STAGE + 1):
        log(f"[report] attempt {attempt}: calling agent...")
        t0 = time.time()
        report_output = run_report_agent(state.analysis_output, feedback=feedback)
        log(f"[report] attempt {attempt}: agent responded in {time.time()-t0:.1f}s")

        det = deterministic.check_report_output(state.analysis_output, report_output)
        result = run_checkpoint(
            state, "report", attempt, report_output, det,
            lambda: llm_checker.check_report(state.analysis_output, report_output),
        )
        if result.passed:
            state.report_output = report_output
            break
        feedback = failure_feedback(result)
    else:
        state.needs_human_review = True
        state.human_review_stage = "report"
        state.human_review_reason = feedback
        return state

    return state


def write_debug_dump(state: PipelineState, path: str) -> None:
    dump = {
        "raw_data_path": state.raw_data_path,
        "needs_human_review": state.needs_human_review,
        "human_review_stage": state.human_review_stage,
        "human_review_reason": state.human_review_reason,
        "checkpoints": [
            {
                "stage": c.stage,
                "attempt": c.attempt,
                "deterministic_passed": c.deterministic_passed,
                "deterministic_reason": c.deterministic_reason,
                "llm_passed": c.llm_passed,
                "llm_reason": c.llm_reason,
                "raw_output": c.raw_output,
            }
            for c in state.checkpoint_history
        ],
        "final_report": state.report_output,
    }
    with open(path, "w") as f:
        json.dump(dump, f, indent=2)
    print(f"Full debug dump written to {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to the raw dataset (CSV)")
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print live progress as each agent call and checkpoint runs",
    )
    parser.add_argument(
        "--debug-out", metavar="PATH",
        help="Write a full JSON dump of every attempt's raw output to this file",
    )
    args = parser.parse_args()

    VERBOSE = args.verbose

    final_state = run_pipeline(args.data)

    print()
    print(final_state.summary())
    print()

    if args.debug_out:
        write_debug_dump(final_state, args.debug_out)

    if final_state.needs_human_review:
        print("Pipeline halted — human review required. See summary above.")
        sys.exit(1)

    print("=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(final_state.report_output)