"""
MCP server skeleton for the data analysis pipeline.

This is a starting point, not a finished server — Person B should flesh out
the tool implementations in src/data_tools.py and src/verify_tools.py.

Reference: https://github.com/modelcontextprotocol/python-sdk
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("data-analysis-tools")


@mcp.tool()
def query_dataset(filter_expr: str, columns: list[str] | None = None) -> dict:
    """
    Query the cleaned dataset with a filter expression.

    TODO (Person B): implement against your actual cleaned dataset.
    Decide how constrained/safe `filter_expr` needs to be.
    """
    raise NotImplementedError


@mcp.tool()
def get_column_summary(column: str) -> dict:
    """
    Return summary stats for a column: dtype, null count, mean/median (if numeric),
    distinct count, and a few sample values.

    TODO (Person B): implement.
    """
    raise NotImplementedError


@mcp.tool()
def run_stat_test(test_name: str, columns: list[str]) -> dict:
    """
    Run a named statistical test (e.g. "correlation", "ttest") on the given columns.
    Returns structured results (not prose) so the analysis agent can reason over them.

    TODO (Person B): implement.
    """
    raise NotImplementedError


@mcp.tool()
def verify_claim(claim: str, column: str, row_refs: list[int] | None = None) -> dict:
    """
    Check a claim made in the draft report against the source data.
    Used by the critic agent to catch hallucinated or unsupported findings.

    TODO (Person B): implement.
    """
    raise NotImplementedError


if __name__ == "__main__":
    mcp.run()
