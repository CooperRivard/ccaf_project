"""
Deterministic checks: cheap, fast, no API call. Run these before the LLM
check so obvious structural problems (missing keys, empty output) never
waste a Claude call.

These are intentionally strict about *shape* (did the agent return what we
asked for) and light on *judgment* (is this a good finding) — judgment is
the LLM checker's job.
"""
import re
from dataclasses import dataclass


@dataclass
class DeterministicResult:
    passed: bool
    reason: str


def check_cleaning_output(output: dict) -> DeterministicResult:
    if "changes_made" not in output or "flagged_for_review" not in output:
        return DeterministicResult(
            False, "Missing required keys 'changes_made' and/or 'flagged_for_review'."
        )
    if not isinstance(output["changes_made"], list) or not isinstance(
        output["flagged_for_review"], list
    ):
        return DeterministicResult(
            False, "'changes_made' and 'flagged_for_review' must be lists."
        )
    for change in output["changes_made"]:
        if not all(k in change for k in ("column", "change", "rows_affected")):
            return DeterministicResult(
                False, f"Malformed entry in changes_made: {change}"
            )
    return DeterministicResult(True, "Structure OK.")


def check_analysis_output(output: dict) -> DeterministicResult:
    if "findings" not in output:
        return DeterministicResult(False, "Missing required key 'findings'.")
    if not isinstance(output["findings"], list) or len(output["findings"]) == 0:
        return DeterministicResult(False, "'findings' must be a non-empty list.")
    for f in output["findings"]:
        required = ("claim", "supporting_evidence", "confidence")
        if not all(k in f for k in required):
            return DeterministicResult(False, f"Finding missing required keys: {f}")
        if f["confidence"] not in ("high", "medium", "low"):
            return DeterministicResult(
                False, f"Invalid confidence value: {f['confidence']!r}"
            )
    return DeterministicResult(True, "Structure OK.")


def _significant_words(text: str) -> set[str]:
    """Words worth checking for coverage — skips short/common words so the
    check isn't thrown off by paraphrasing, only by genuinely missing content."""
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "was", "were", "is", "are", "this", "that", "during",
        "one", "instance", "which", "not", "collectively", "affecting",
    }
    words = re.findall(r"[a-z0-9.]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in stopwords}


def check_report_output(findings: dict, report_text: str) -> DeterministicResult:
    if not report_text or len(report_text.strip()) < 50:
        return DeterministicResult(False, "Report is empty or suspiciously short.")
    if "# " not in report_text and "## " not in report_text:
        return DeterministicResult(False, "Report has no markdown headers.")

    # Every high-confidence finding should be reflected in the report — but the
    # report is expected to PARAPHRASE, not quote the claim verbatim. So instead
    # of exact substring matching, check word-overlap coverage: does a decent
    # fraction of the claim's distinctive words (numbers, IDs, key terms) show
    # up somewhere in the report? This tolerates rewording while still catching
    # a report that silently drops a finding entirely.
    high_conf_claims = [
        f["claim"] for f in findings.get("findings", []) if f.get("confidence") == "high"
    ]
    report_words = _significant_words(report_text)

    missing = []
    for claim in high_conf_claims:
        claim_words = _significant_words(claim)
        if not claim_words:
            continue
        coverage = len(claim_words & report_words) / len(claim_words)
        if coverage < 0.4:
            missing.append((claim, round(coverage, 2)))

    if missing:
        return DeterministicResult(
            False,
            f"{len(missing)} high-confidence finding(s) don't appear to be "
            f"reflected in the report text: {missing}",
        )
    return DeterministicResult(True, "Structure OK.")