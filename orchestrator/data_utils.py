"""
Phase 1 helper: gives worker agents a data preview directly in the prompt,
so you can test the orchestration/checkpoint logic end-to-end before
Person B's MCP server exists.

Phase 2 TODO: once mcp-server/ is ready, worker agents should use MCP tools
(query_dataset, get_column_summary, etc.) to explore data on demand instead
of receiving a static preview. Swap that in agents/*.py — this file can stay
as a fallback/debugging aid even after that.
"""
import pandas as pd


def quick_data_preview(csv_path: str, max_rows: int = 10) -> str:
    """Returns a compact textual summary of a CSV: shape, dtypes, nulls, head."""
    df = pd.read_csv(csv_path)

    lines = [
        f"Dataset: {csv_path}",
        f"Shape: {df.shape[0]} rows x {df.shape[1]} columns",
        "",
        "Columns (name: dtype, null count):",
    ]
    for col in df.columns:
        lines.append(f"  - {col}: {df[col].dtype}, {df[col].isnull().sum()} nulls")

    lines.append("")
    lines.append(f"First {max_rows} rows:")
    lines.append(df.head(max_rows).to_string())

    return "\n".join(lines)
