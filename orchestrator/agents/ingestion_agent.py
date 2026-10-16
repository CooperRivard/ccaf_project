"""
Ingestion/cleaning agent. Phase 1: works off a text data preview.
Phase 2 TODO: give it MCP tools (e.g. query_dataset, get_column_summary)
so it can explore the full dataset rather than just the preview.
"""
from ..utils import load_system_prompt, parse_json_response
from .base_agent import BaseAgent


def run_ingestion_agent(data_preview: str, feedback: str | None = None) -> dict:
    system_prompt = load_system_prompt("ingestion_agent.md")
    agent = BaseAgent(name="ingestion", system_prompt=system_prompt)

    user_message = f"Here is the raw dataset:\n\n{data_preview}"
    if feedback:
        user_message += (
            f"\n\nNOTE: a previous attempt was rejected. Feedback to address:\n{feedback}"
        )

    raw_response = agent.run(user_message)
    return parse_json_response(raw_response)
