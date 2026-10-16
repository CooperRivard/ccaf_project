"""Small shared helpers."""
import json
import re
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_system_prompt(filename: str) -> str:
    """
    Loads a prompt markdown file from /prompts (owned by Person C).
    Loading it fresh each run (rather than hardcoding prompts in Python)
    means Person C can iterate on prompts without touching orchestrator code.
    """
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}. Has Person C written {filename} yet?"
        )
    return path.read_text()


def parse_json_response(text: str) -> dict:
    """
    Parses a JSON object out of a model response, tolerating markdown code
    fences (```json ... ```) since models sometimes add them even when told
    not to.
    """
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Could not parse JSON from model response. Raw response:\n{text}"
        ) from e
