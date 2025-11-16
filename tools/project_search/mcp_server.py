"""
MCP server exposing a project search tool that surfaces file snippets.
"""
import json
import sys
from typing import Any, Dict

from .search import search

TOOL_DEFINITION: Dict[str, Any] = {
    "name": "project_search",
    "description": "Search project files for keywords and return file paths with contextual snippets.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search term or regex supported by ripgrep. Example: 'ProjectBrief' or 'class .*Agent'.",
            },
            "file_globs": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional glob filters (e.g., ['src/**/*.py', 'docs/*.md'])",
            },
            "max_results": {
                "type": "integer",
                "default": 5,
                "description": "Maximum number of matches to return (1-25).",
            },
            "context_lines": {
                "type": "integer",
                "default": 2,
                "description": "How many lines of context to include before/after the match (0-10).",
            },
            "case_sensitive": {
                "type": "boolean",
                "default": False,
                "description": "Set true to make the search case sensitive.",
            },
        },
        "required": ["query"],
    },
}


def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    method = request.get("method")

    if method == "tools/list":
        return {"tools": [TOOL_DEFINITION]}

    if method == "tools/call":
        tool_name = request["params"]["name"]
        arguments = request["params"].get("arguments", {})

        if tool_name != "project_search":
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            return search(**arguments)
        except Exception as exc:  # pragma: no cover - surface error as JSON
            return {"error": str(exc)}

    return {"error": f"Unknown method: {method}"}


if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON request"}))
            sys.stdout.flush()
            continue

        response = handle_request(request)
        print(json.dumps(response, ensure_ascii=False))
        sys.stdout.flush()

