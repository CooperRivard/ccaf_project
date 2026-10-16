"""
Shared agent wrapper: handles the call-to-Claude + optional tool-use loop.

Phase 1 (now): worker agents get data via a text preview in the prompt
(see ../data_utils.py), so `tools`/`tool_executor` are unused. This lets you
test the full orchestration/checkpoint flow without Person B's MCP server.

Phase 2 (once mcp-server/ is ready): pass `tools` (the MCP tool schemas) and
a `tool_executor` callable that dispatches tool_use blocks to the MCP server.
The loop below already handles that path — swap it in per-agent in
ingestion_agent.py / analysis_agent.py / report_agent.py, coordinate with
Person B on the exact tool schemas.
"""
from typing import Callable

import anthropic

from ..config import WORKER_MODEL

client = anthropic.Anthropic()


class BaseAgent:
    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str = WORKER_MODEL,
        tools: list | None = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools or []

    def run(
        self,
        user_message: str,
        tool_executor: Callable[[str, dict], dict] | None = None,
        max_tool_iterations: int = 10,
    ) -> str:
        """
        Runs the agent loop until Claude stops asking for tools
        (stop_reason != "tool_use") or max_tool_iterations is hit.
        Returns the final text response.
        """
        messages = [{"role": "user", "content": user_message}]

        for _ in range(max_tool_iterations):
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=messages,
                tools=self.tools if self.tools else anthropic.NOT_GIVEN,
            )

            if response.stop_reason != "tool_use":
                return "".join(
                    block.text for block in response.content if block.type == "text"
                )

            if tool_executor is None:
                raise RuntimeError(
                    f"[{self.name}] Model requested a tool but no tool_executor "
                    f"was provided. Phase 1 agents shouldn't have tools configured "
                    f"— check that self.tools is empty, or wire up Phase 2 (MCP)."
                )

            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = tool_executor(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        }
                    )
            messages.append({"role": "user", "content": tool_results})

        raise RuntimeError(f"[{self.name}] exceeded max_tool_iterations without finishing")
