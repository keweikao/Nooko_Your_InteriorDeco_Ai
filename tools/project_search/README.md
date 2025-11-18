# Project Search MCP Server

This MCP server exposes a `project_search` tool that helps any AI assistant quickly locate relevant files and snippets inside this repository without scanning the filesystem manually.

## Features

- Keyword / regex search powered by `ripgrep`
- Optional glob filters to narrow the results (`src/**/*.py`, `docs/*.md`, …)
- Configurable match limit (default 5, max 25)
- Adjustable context lines (default 2) with snippets that include line numbers
- Case-insensitive search by default (toggle via `case_sensitive: true`)

## Usage

1. Ensure `rg` (ripgrep) is installed and available on the `$PATH`.
2. (Optional) Set `PROJECT_SEARCH_ROOT` to override the default repository root.
3. Register the MCP server in `~/.claude/mcp_config.json`:

```jsonc
{
  "mcpServers": {
    "project_search": {
      "command": "python3",
      "args": [
        "/Users/stephen/Desktop/HouseIQ_Your_InteriorDeco_Ai/tools/project_search/mcp_server.py"
      ],
      "env": {
        "PROJECT_SEARCH_ROOT": "/Users/stephen/Desktop/HouseIQ_Your_InteriorDeco_Ai"
      },
      "disabled": false
    }
  }
}
```

4. In your MCP-enabled client (Claude Desktop, Claude Code, etc.), call the `project_search` tool:

```jsonc
{
  "name": "project_search",
  "arguments": {
    "query": "ProjectBrief",
    "file_globs": ["analysis-service/**/*.py"],
    "max_results": 3,
    "context_lines": 2
  }
}
```

The tool responds with JSON containing the relative file path, line number, and a snippet for each match so that the AI can immediately read the relevant section without issuing multiple filesystem reads.

## Notes

- Respect the `max_results` to keep responses small and token-efficient.
- Use glob filters whenever possible; this keeps searches fast and scoped to the files you actually need.
- If you frequently switch repositories, override `PROJECT_SEARCH_ROOT` per session to ensure searches run in the correct directory.

