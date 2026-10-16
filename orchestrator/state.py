"""
Tracks state as it moves through the pipeline: what each agent produced,
what the orchestrator's checks found, and how many retries each stage used.

Keeping this as an explicit object (rather than passing loose dicts around)
is the context-management story for this project: it's the single source of
truth for what gets shown to which agent, and it's what you'd point to if
asked in the exam "how do you manage context across a multi-agent pipeline."
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckpointResult:
    stage: str
    attempt: int
    deterministic_passed: bool
    deterministic_reason: str
    llm_passed: bool | None  # None if LLM check was skipped
    llm_reason: str | None
    raw_output: Any = None  # the agent's actual output for this attempt, for debugging

    @property
    def passed(self) -> bool:
        if not self.deterministic_passed:
            return False
        if self.llm_passed is None:
            return True
        return self.llm_passed


@dataclass
class PipelineState:
    raw_data_path: str

    # Outputs from each stage (None until that stage completes)
    cleaning_output: dict[str, Any] | None = None
    analysis_output: dict[str, Any] | None = None
    report_output: str | None = None

    # Full history of every checkpoint attempt, across every stage.
    # This is what you'd show a teammate (or an exam grader) to justify
    # "the orchestrator caught X and retried Y."
    checkpoint_history: list[CheckpointResult] = field(default_factory=list)

    # Set to True if a stage exhausts its retries and needs a human.
    needs_human_review: bool = False
    human_review_stage: str | None = None
    human_review_reason: str | None = None

    def record_checkpoint(self, result: CheckpointResult) -> None:
        self.checkpoint_history.append(result)

    def retries_used(self, stage: str) -> int:
        return sum(1 for c in self.checkpoint_history if c.stage == stage)

    def summary(self) -> str:
        lines = [f"Pipeline run for: {self.raw_data_path}", ""]
        for c in self.checkpoint_history:
            status = "PASS" if c.passed else "FAIL"
            lines.append(
                f"  [{c.stage}] attempt {c.attempt}: {status} "
                f"(deterministic={c.deterministic_passed}, llm={c.llm_passed})"
            )
        if self.needs_human_review:
            lines.append("")
            lines.append(
                f"NEEDS HUMAN REVIEW at stage '{self.human_review_stage}': "
                f"{self.human_review_reason}"
            )
        return "\n".join(lines)