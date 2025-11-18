#!/usr/bin/env python3
"""
GCP Operations MCP Server

Expose frequently used GCP inspection commands (Cloud Run, Cloud Build, Cloud Logging)
via MCP so that investigators can quickly pull service state without leaving the CLI.
Each tool wraps `gcloud` commands and returns JSON responses.
"""
import json
import os
import subprocess
import sys
from typing import Dict, Any, List

DEFAULT_PROJECT = (
    os.environ.get("GCP_PROJECT")
    or os.environ.get("GOOGLE_CLOUD_PROJECT")
    or os.environ.get("PROJECT_ID")
)
DEFAULT_REGION = os.environ.get("GCP_REGION", "us-central1")


def _run_gcloud(args: List[str]) -> Dict[str, Any]:
    """Run a gcloud command and return JSON stdout or error."""
    cmd = ["gcloud"] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {
            "error": "Command failed",
            "command": " ".join(cmd),
            "stderr": result.stderr.strip(),
        }
    stdout = result.stdout.strip()
    if not stdout:
        return {"result": "Command executed successfully (no output)"}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def describe_cloud_run_service(service_name: str, region: str = None, project_id: str = None) -> Dict[str, Any]:
    """Describe a Cloud Run service."""
    region = region or DEFAULT_REGION
    project = project_id or DEFAULT_PROJECT
    args = ["run", "services", "describe", service_name, f"--region={region}", "--format=json"]
    if project:
        args.append(f"--project={project}")
    return _run_gcloud(args)


def list_cloud_builds(limit: int = 5, status: str = None, project_id: str = None) -> Dict[str, Any]:
    """List recent Cloud Build jobs."""
    project = project_id or DEFAULT_PROJECT
    args = ["builds", "list", f"--limit={limit}", "--format=json"]
    if status:
        args.append(f"--filter=status={status}")
    if project:
        args.append(f"--project={project}")
    return _run_gcloud(args)


def read_cloud_run_logs(service_name: str, limit: int = 20, project_id: str = None) -> Dict[str, Any]:
    """Read recent Cloud Logging entries for a Cloud Run service."""
    project = project_id or DEFAULT_PROJECT
    filter_expr = (
        f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}"'
    )
    args = [
        "logging",
        "read",
        filter_expr,
        f"--limit={limit}",
        "--format=json",
    ]
    if project:
        args.append(f"--project={project}")
    return _run_gcloud(args)


TOOLS = [
    {
        "name": "cloud_run_describe",
        "description": "Describe a Cloud Run service (uses gcloud run services describe)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
                "region": {"type": "string", "default": DEFAULT_REGION},
                "project_id": {"type": "string", "default": DEFAULT_PROJECT},
            },
            "required": ["service_name"],
        },
    },
    {
        "name": "cloud_builds_list",
        "description": "List recent Cloud Build jobs (gcloud builds list)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 5},
                "status": {"type": "string", "description": "Filter by build status"},
                "project_id": {"type": "string", "default": DEFAULT_PROJECT},
            },
        },
    },
    {
        "name": "cloud_run_logs",
        "description": "Fetch recent Cloud Logging entries for a Cloud Run service",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
                "project_id": {"type": "string", "default": DEFAULT_PROJECT},
            },
            "required": ["service_name"],
        },
    },
]


def handle_request(request: dict) -> dict:
    method = request.get("method")

    if method == "tools/list":
        return {"tools": TOOLS}
    elif method == "tools/call":
        tool_name = request["params"]["name"]
        arguments = request["params"].get("arguments", {})

        if tool_name == "cloud_run_describe":
            return describe_cloud_run_service(**arguments)
        if tool_name == "cloud_builds_list":
            return list_cloud_builds(**arguments)
        if tool_name == "cloud_run_logs":
            return read_cloud_run_logs(**arguments)
        return {"error": f"Unknown tool: {tool_name}"}
    else:
        return {"error": f"Unknown method: {method}"}


if __name__ == "__main__":
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
        except Exception as exc:  # pragma: no cover - defensive logging
            error_response = {"error": str(exc)}
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()
