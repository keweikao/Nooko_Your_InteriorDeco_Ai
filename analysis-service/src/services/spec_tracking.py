from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple


@dataclass(frozen=True)
class SpecField:
    field_id: str
    label: str
    category: str
    required: bool = True
    min_confidence: float = 0.75
    priority: int = 3


SPEC_FIELDS: List[SpecField] = [
    SpecField("user_name", "稱呼", "greeting", required=True, min_confidence=0.6, priority=1),
    SpecField("project_type", "裝修範圍", "scope", required=True, priority=0),
    SpecField("focus_areas", "重點空間", "scope"),
    SpecField("total_area", "坪數/面積", "scope"),
    SpecField("space_usage", "空間用途", "lifestyle"),
    SpecField("house_condition", "屋況/年齡", "lifestyle"),
    SpecField("family_profile", "家庭成員", "lifestyle", required=False, min_confidence=0.5),
    SpecField("budget_range", "預算區間", "budget", priority=0),
    SpecField("budget_scope", "預算是否含家電/家具", "budget", required=False, min_confidence=0.6),
    SpecField("timeline", "時程壓力", "timeline"),
    SpecField("priority", "品質/外觀/預算優先順序", "timeline", required=False),
    SpecField("style_preference", "風格偏好", "style"),
    SpecField("lighting_storage", "照明/收納需求", "style", required=False),
    SpecField("material_preference", "材料偏好", "style", required=False),
    SpecField("quality_level", "品質等級", "style", required=False),
    SpecField("special_requirements", "特殊需求/限制", "construction", required=False, min_confidence=0.5),
    SpecField("risk_flags", "疑似風險", "construction", required=False, min_confidence=0.4),
]


STAGE_THRESHOLDS: List[Tuple[str, int]] = [
    ("greeting", 0),
    ("scope", 20),
    ("lifestyle", 40),
    ("budget", 60),
    ("construction", 80),
    ("summary", 100),
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
        payload = {k: v for k, v in incoming.items() if k != "confidence_scores"}
        confidence_scores = incoming.get("confidence_scores", {})
        changed = False

        for field_id, value in payload.items():
            if field_id not in self.field_lookup:
                continue  # 非追蹤欄位
            if value in (None, "", []):
                continue

            confidence = confidence_scores.get(field_id, 0.6)
            previous = state.get(field_id, {})
            if confidence >= previous.get("confidence", 0):
                state[field_id] = {
                    "value": value,
                    "confidence": confidence,
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
        return sorted(missing, key=lambda item: (item["priority"], item["label"]))

    @staticmethod
    def _is_field_satisfied(entry: Dict[str, Any] | None, field: SpecField) -> bool:
        if not entry:
            return False
        return entry.get("confidence", 0.0) >= field.min_confidence
