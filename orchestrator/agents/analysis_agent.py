"""
Analysis agent. Phase 1: works off a text data preview + the cleaning
agent's summary of what changed. Phase 2 TODO: give it MCP tools
(query_dataset, run_stat_test, get_column_summary) for real exploration.
"""
from ..utils import load_system_prompt, parse_json_response
from .base_agent import BaseAgent


def run_analysis_agent(
    data_preview: str, cleaning_output: dict, feedback: str | None = None
) -> dict:
    system_prompt = load_system_prompt("analysis_agent.md")
    agent = BaseAgent(name="analysis", system_prompt=system_prompt)

    user_message = (
        f"Here is the cleaned dataset (preview):\n\n{data_preview}\n\n"
        f"Cleaning summary (what was changed):\n{cleaning_output}"
    )
    if feedback:
        user_message += (
            f"\n\nNOTE: a previous attempt was rejected. Feedback to address:\n{feedback}"
        )

    raw_response = agent.run(user_message)
    return parse_json_response(raw_response)
