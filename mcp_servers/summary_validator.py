from mcp.server.fastmcp import FastMCP
from pathlib import Path

mcp = FastMCP("summary-validator")

REQUIRED_SECTIONS = [
    "## Overview",
    "## Description",
    "## Analysis",
    "## Related Issues",
    "## Slack Discussions",
    "## GitHub Issues",
    "## Comments",
    "## Update Log",
]


@mcp.tool()
async def validate_summary(issue_key: str) -> dict:
    """Validates that the generated summary.md for an issue exists and has all required sections"""
    path = Path(f"issues/{issue_key}/summary.md")

    if not path.exists():
        return {"valid": False, "error": "summary.md not found", "missing_sections": REQUIRED_SECTIONS}

    content = path.read_text()
    missing = [s for s in REQUIRED_SECTIONS if s not in content]

    return {
        "valid": len(missing) == 0,
        "missing_sections": missing,
        "word_count": len(content.split()),
        "content": content,
    }


if __name__ == "__main__":
    mcp.run()