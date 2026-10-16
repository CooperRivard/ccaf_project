"""Report-writer agent. Takes structured findings, produces the markdown report."""
from ..utils import load_system_prompt
from .base_agent import BaseAgent


def run_report_agent(analysis_output: dict, feedback: str | None = None) -> str:
    system_prompt = load_system_prompt("report_writer.md")
    agent = BaseAgent(name="report_writer", system_prompt=system_prompt)

    user_message = f"Here are the structured findings:\n\n{analysis_output}"
    if feedback:
        user_message += (
            f"\n\nNOTE: a previous attempt was rejected. Feedback to address:\n{feedback}"
        )

    return agent.run(user_message)  # report is plain markdown text, not JSON
