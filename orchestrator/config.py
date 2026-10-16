"""Orchestrator configuration."""

# Model used for worker agents (ingestion, analysis, report)
WORKER_MODEL = "claude-sonnet-4-6"

# Model used for the orchestrator's own LLM-based checkpoint judgments.
# Deliberately separate from WORKER_MODEL so the team can experiment with
# using a cheaper/faster model for checking vs. the model doing the real work.
CHECKER_MODEL = "claude-sonnet-4-6"

# How many times to retry a stage (send back to the same agent with feedback)
# before escalating to human review.
MAX_RETRIES_PER_STAGE = 3

# If True, run the LLM-based checkpoint judgment after deterministic checks pass.
# If False, deterministic checks alone gate progression (useful for fast iteration
# while deterministic checks are still being tuned).
ENABLE_LLM_CHECKS = True
