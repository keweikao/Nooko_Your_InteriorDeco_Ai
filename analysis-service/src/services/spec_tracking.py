from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple


@dataclass(frozen=True)
class SpecField:
    """Represents a stage in the conversational flow that needs to be completed."""
    field_id: str
    label: str
    # 'category' and 'priority' can be used to group and order the stages.
    category: str
    priority: int
    # All stages are required by default in this new flow.
    required: bool = True
    # Confidence will be manually set to 1.0 when a stage is deemed complete.
    min_confidence: float = 0.95


# New SPEC_FIELDS based on the 5-stage conversational flow
SPEC_FIELDS: List[SpecField] = [
    SpecField("stage_1_situation_purpose", "釐清屋況與使用目的", "collection", priority=1),
    SpecField("stage_2_scope_condition", "釐清施工範圍與現況", "collection", priority=2),
    SpecField("stage_3_material_style", "釐清材質與風格偏好", "collection", priority=3),
    SpecField("stage_4_hidden_risks", "釐清隱藏工程與風險", "collection", priority=4),
    SpecField("stage_5_budget_decision", "確認預算感與決策方式", "collection", priority=5),
]

# New STAGE_THRESHOLDS to reflect the progress through the 5 stages
STAGE_THRESHOLDS: List[Tuple[str, int]] = [
    ("start", 0),
    ("situation_purpose", 20),  # After stage 1 is complete (1/5)
    ("scope_condition", 40),   # After stage 2 is complete (2/5)
    ("material_style", 60),    # After stage 3 is complete (3/5)
    ("hidden_risks", 80),      # After stage 4 is complete (4/5)
    ("summary", 100),          # After stage 5 is complete (5/5)
]


class SpecTracker:
    """
    欄位追蹤器：集中管理對話期間蒐集到的資訊，
    提供 merge/evaluate 能力以回傳 stage/missing fields，
    供 SSE metadata、Gemini prompt 與完成檢查使用。
    """

    def __init__(self, fields: List[SpecField] | None = None):
        self.fields = fields or SPEC_FIELDS
        self.field_lookup = {field.field_id: field for field in self.fields}
        self.required_ids = [field.field_id for field in self.fields if field.required]

    def empty_state(self) -> Dict[str, Any]:
        return {}

    def initial_missing_fields(self) -> List[Dict[str, Any]]:
        return self._build_missing_fields({})

    def merge(self, state: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        """
        將 LLM 提取結果合併至現有 state 並回傳進度評估。
        Input: state=Firestore 既有欄位, incoming=Gemini JSON。
        Output: dict 包含更新後 state、progress、stage、missing_fields。
        """
        state = dict(state or {})
        # In the new logic, 'incoming' will contain stage completion flags, e.g., {"stage_1_situation_purpose": true}
        payload = {k: v for k, v in incoming.items() if k in self.field_lookup}
        changed = False

        for field_id, value in payload.items():
            # If the incoming value is truthy, it means the stage is complete.
            if value and not self._is_field_satisfied(state.get(field_id), self.field_lookup[field_id]):
                state[field_id] = {
                    "value": "completed", # Store a simple marker
                    "confidence": 1.0,    # Mark with full confidence
                    "updated_at": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
                }
                changed = True

        evaluation = self.evaluate(state)
        evaluation["state"] = state
        evaluation["changed"] = changed
        return evaluation

    def evaluate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        針對現有 state 計算 stage/progress/missing_fields，
        供 SSE metadata 或完成檢查使用。
        """
        state = state or {}
        completed = sum(
            1 for field_id in self.required_ids
            if self._is_field_satisfied(state.get(field_id), self.field_lookup[field_id])
        )
        total = len(self.required_ids)
        progress = int((completed / total) * 100) if total else 100
        stage = self._stage_from_progress(progress)
        missing_fields = self._build_missing_fields(state)

        return {
            "progress": progress,
            "stage": stage,
            "missing_fields": missing_fields,
            "completed": completed,
            "total_required": total,
        }

    def _stage_from_progress(self, progress: int) -> str:
        current_stage = STAGE_THRESHOLDS[0][0]
        for stage_name, threshold in STAGE_THRESHOLDS:
            if progress >= threshold:
                current_stage = stage_name
        return current_stage

    def _build_missing_fields(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        missing = []
        for field in self.fields:
            entry = state.get(field.field_id)
            if not self._is_field_satisfied(entry, field):
                missing.append({
                    "id": field.field_id,
                    "label": field.label,
                    "category": field.category,
                    "priority": field.priority,
                    "minConfidence": field.min_confidence,
                })
        # Return the next stage to be completed
        return sorted(missing, key=lambda item: item["priority"])

    @staticmethod
    def _is_field_satisfied(entry: Dict[str, Any] | None, field: SpecField) -> bool:
        if not entry:
            return False
        # Check for a confidence score that meets the minimum requirement
        return entry.get("confidence", 0.0) >= field.min_confidence
