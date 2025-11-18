"""
Utility functions for searching project files via ripgrep.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_MAX_RESULTS = 5
MAX_RESULTS_LIMIT = 25
DEFAULT_CONTEXT_LINES = 2
MAX_CONTEXT_LINES = 10

_FILE_CACHE: Dict[Path, List[str]] = {}


def _project_root() -> Path:
    """Return the root directory to search."""
    env_root = os.environ.get("PROJECT_SEARCH_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def _ensure_ripgrep_available() -> None:
    if shutil.which("rg") is None:
        raise RuntimeError(
            "Missing dependency: ripgrep (rg). Please install it so the project search MCP server can execute queries."
        )


def _load_file_lines(path: Path) -> List[str]:
    cached = _FILE_CACHE.get(path)
    if cached is not None:
        return cached

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover - best effort logging
        raise RuntimeError(f"Unable to read file for snippet generation: {path}") from exc

    lines = text.splitlines()
    _FILE_CACHE[path] = lines
    return lines


def _build_snippet(path: Path, line_number: int, context_lines: int) -> str:
    lines = _load_file_lines(path)
    if not lines:
        return ""

    idx = max(0, min(len(lines) - 1, line_number - 1))

    if context_lines <= 0:
        return f">{idx + 1}: {lines[idx]}"

    start = max(0, idx - context_lines)
    end = min(len(lines) - 1, idx + context_lines)

    snippet_parts: List[str] = []
    for i in range(start, end + 1):
        prefix = ">" if i == idx else " "
        line_text = lines[i]
        snippet_parts.append(f"{prefix}{i + 1}: {line_text}")
    return "\n".join(snippet_parts)


def search(
    query: str,
    file_globs: Optional[List[str]] = None,
    max_results: int = DEFAULT_MAX_RESULTS,
    context_lines: int = DEFAULT_CONTEXT_LINES,
    case_sensitive: bool = False,
) -> Dict[str, object]:
    """Search project files for the query and return structured snippets."""
    if not query or not query.strip():
        raise ValueError("query is required.")

    _ensure_ripgrep_available()

    base_path = _project_root()
    if not base_path.exists():
        raise RuntimeError(f"Project root does not exist: {base_path}")

    sanitized_max = max(1, min(max_results or DEFAULT_MAX_RESULTS, MAX_RESULTS_LIMIT))
    sanitized_context = max(0, min(context_lines or DEFAULT_CONTEXT_LINES, MAX_CONTEXT_LINES))

    cmd = [
        "rg",
        "--json",
        "--line-number",
    ]
    if not case_sensitive:
        cmd.append("-i")

    globs = file_globs or []
    for glob in globs:
        if glob:
            cmd.extend(["--glob", glob])

    cmd.extend(["--", query, str(base_path)])

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    results = []
    has_more = False

    assert process.stdout is not None  # for mypy
    for line in process.stdout:
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue

        if payload.get("type") != "match":
            continue

        data = payload.get("data", {})
        path_text = data.get("path", {}).get("text")
        if not path_text:
            continue

        match_path = Path(path_text)
        if not match_path.is_absolute():
            match_path = (base_path / match_path).resolve()

        line_number = int(data.get("line_number", 0))
        match_line = data.get("lines", {}).get("text", "").rstrip("\n")
        submatches = data.get("submatches") or []
        snippet = ""
        try:
            snippet = _build_snippet(match_path, line_number, sanitized_context)
        except Exception:
            snippet = match_line

        relative_path = str(match_path.relative_to(base_path))
        match_entry = {
            "file": relative_path,
            "line": line_number,
            "match_line": match_line,
            "snippet": snippet,
        }
        if submatches:
            match_entry["matched_text"] = submatches[0].get("match", {}).get("text")

        results.append(match_entry)

        if len(results) >= sanitized_max:
            has_more = True
            break

    if len(results) >= sanitized_max:
        process.kill()
    stdout = process.stdout
    stdout.close()
    stderr_data = ""
    if process.stderr:
        stderr_data = process.stderr.read().strip()
        process.stderr.close()
    process.wait()

    if process.returncode not in (0, 1, -9, None) and not results:
        raise RuntimeError(stderr_data or "ripgrep failed to execute search.")

    return {
        "query": query,
        "base_path": str(base_path),
        "results": results,
        "result_count": len(results),
        "has_more": has_more,
        "notes": "Use file_globs to restrict the search scope and reduce token usage.",
    }
