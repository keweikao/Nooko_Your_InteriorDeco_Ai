import os
import sys

from typing import Dict, Any, List

import pytest

# 確保分析服務根目錄在 sys.path 中，讓 `src` 套件可被載入
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")

for path in (ROOT_DIR, SRC_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from src.api import projects  # noqa: E402  pylint: disable=C0413


class ConversationServiceTestDouble:
    """Minimal stub to avoid hitting real Firestore during tests."""

    def __init__(self):
        self.created_projects = set()
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.spec_state: Dict[str, Dict[str, Any]] = {}
        self.missing: Dict[str, List[Dict[str, Any]]] = {}
        self.stage_state: Dict[str, Dict[str, Any]] = {}

    async def create_project_in_db(self, project_id: str) -> None:
        self.created_projects.add(project_id)

    async def project_exists(self, project_id: str) -> bool:
        return project_id in self.created_projects or project_id.startswith("test")

    async def create_conversation(self, conversation_id: str, project_id: str):
        conv = {"conversation_id": conversation_id, "project_id": project_id}
        self.conversations[conversation_id] = conv
        return conv

    async def get_project_conversation(self, project_id: str):
        for conv in self.conversations.values():
            if conv["project_id"] == project_id:
                return conv
        return None

    async def save_message(self, *args, **kwargs):
        return "msg-id"

    async def update_extracted_specs(self, *args, **kwargs):
        conversation_id, specs = args[0], args[1]
        self.spec_state[conversation_id] = specs

    async def get_current_specs(self, conversation_id: str):
        return self.spec_state.get(conversation_id, {})

    async def update_missing_fields(self, conversation_id: str, missing_fields):
        self.missing[conversation_id] = missing_fields

    async def get_missing_fields(self, conversation_id: str):
        return self.missing.get(conversation_id, [])

    async def update_conversation_stage(self, conversation_id: str, stage: str, progress: int):
        self.stage_state[conversation_id] = {"stage": stage, "progress": progress}

    async def log_event(self, *args, **kwargs):
        return None


@pytest.fixture(autouse=True)
def patch_conversation_service(monkeypatch):
    """
    Provide a default stub so tests don't connect to Firestore.
    Individual tests can monkeypatch again if needed.
    """
    service = ConversationServiceTestDouble()
    monkeypatch.setattr(projects, "conversation_service", service)
    yield service
