"""
LLM-based checkpoint checks: only runs after deterministic checks pass.
This is where the orchestrator catches things code can't — a cleaning
decision that changed the meaning of data, a finding that sounds plausible
but isn't actually supported, a report that drops a caveat.

This is intentionally a separate, narrowly-scoped Claude call per checkpoint
rather than one general "critic agent" — each call gets exactly the context
it needs to judge one specific handoff, which keeps context small and the
judgment focused. See docs/architecture.md section 4 for the reasoning.
"""
from dataclasses import dataclass

import anthropic

from . import deterministic  # noqa: F401  (kept for import symmetry / future shared types)
from ..config import CHECKER_MODEL

client = anthropic.Anthropic()

CHECKER_SYSTEM_PROMPT = """You are a strict quality checkpoint inside a data \
analysis pipeline. You will be shown what an agent was asked to do, what it \
was given as input, and what it produced. Your only job is to judge whether \
the output is a faithful, well-supported result of that input — not to redo \
the work yourself.

Respond with ONLY valid JSON in this exact schema, no other text:
{"passed": true or false, "reason": "one or two sentences explaining your judgment"}

Be skeptical. Flag anything that looks fabricated, unsupported, or that \
silently drops caveats/uncertainty present in the input."""


@dataclass
class LLMCheckResult:
    passed: bool
    reason: str


def _run_checker(task_description: str, input_summary: str, output_summary: str) -> LLMCheckResult:
    user_message = (
        f"Task: {task_description}\n\n"
        f"--- INPUT ---\n{input_summary}\n\n"
        f"--- OUTPUT TO JUDGE ---\n{output_summary}"
    )
    response = client.messages.create(
        model=CHECKER_MODEL,
        max_tokens=512,
        system=CHECKER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")

    import json
    import re

    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    parsed = json.loads(cleaned)
    return LLMCheckResult(passed=bool(parsed["passed"]), reason=parsed["reason"])


def check_cleaning(data_preview: str, cleaning_output: dict) -> LLMCheckResult:
    return _run_checker(
        task_description="Clean a raw dataset: fix type/format issues, dedupe, "
        "flag ambiguous cases instead of guessing. Judge whether the changes "
        "made are reasonable and nothing was silently altered without being logged.",
        input_summary=data_preview,
        output_summary=str(cleaning_output),
    )


def check_analysis(cleaned_data_preview: str, analysis_output: dict) -> LLMCheckResult:
    return _run_checker(
        task_description="Analyze cleaned data and produce findings, each with "
        "supporting evidence and a confidence level. Judge whether each finding's "
        "supporting_evidence plausibly justifies its claim and confidence level.",
        input_summary=cleaned_data_preview,
        output_summary=str(analysis_output),
    )


def check_report(analysis_output: dict, report_text: str) -> LLMCheckResult:
    return _run_checker(
        task_description="Write a human-readable report from structured findings. "
        "Judge whether the report accurately reflects the findings — including "
        "confidence levels and caveats — without overstating or fabricating anything.",
        input_summary=str(analysis_output),
        output_summary=report_text,
    )
