from google.cloud import firestore
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    """Firestore 持久化對話服務"""

    def __init__(self):
        self.db = firestore.AsyncClient()
        self.conversations_col = self.db.collection("conversations")

    async def create_conversation(
        self,
        conversation_id: str,
        project_id: str
    ) -> Dict[str, Any]:
        """初始化新的對話會話"""
        data = {
            "conversation_id": conversation_id,
            "project_id": project_id,
            "stage": "greeting",
            "progress": 0,
            "message_count": 0,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        await self.conversations_col.document(conversation_id).set(data)
        return data

    async def save_message(
        self,
        conversation_id: str,
        sender: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """保存單一消息到 Firestore，並支持自訂消息類型"""
        doc_ref, message_ref = await self.conversations_col.document(
            conversation_id
        ).collection("messages").add({
            "sender": sender,
            "content": content,
            "type": message_type, # Add message type field
            "timestamp": firestore.SERVER_TIMESTAMP,
            "metadata": metadata or {}
        })

        # 增加消息計數
        await self.conversations_col.document(conversation_id).update({
            "message_count": firestore.Increment(1),
            "updated_at": firestore.SERVER_TIMESTAMP
        })

        return message_ref.id

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """檢索完整的對話歷史（用於傳遞給LLM）"""
        messages_ref = self.conversations_col.document(
            conversation_id
        ).collection("messages").order_by(
            "timestamp",
            direction=firestore.Query.ASCENDING
        ).limit(limit)

        docs = messages_ref.stream()
        messages: List[Dict[str, Any]] = []
        async for doc in docs:
            data = doc.to_dict() or {}
            messages.append({
                "id": doc.id,
                "sender": data.get("sender"),
                "content": data.get("content"),
                "timestamp": data.get("timestamp"),
                "metadata": data.get("metadata", {})
            })
        return messages

    async def update_extracted_specs(
        self,
        conversation_id: str,
        specs: Dict[str, Any]
    ) -> None:
        """更新當前會話的已提取規格"""
        await self.conversations_col.document(
            conversation_id
        ).collection("extracted_specs").document(
            "current_version"
        ).set(specs, merge=True)

    async def update_conversation_stage(
        self,
        conversation_id: str,
        stage: str,
        progress: int
    ) -> None:
        """更新對話進度和階段"""
        await self.conversations_col.document(conversation_id).update({
            "stage": stage,
            "progress": progress,
            "updated_at": firestore.SERVER_TIMESTAMP
        })

    async def update_missing_fields(
        self,
        conversation_id: str,
        missing_fields: List[Dict[str, Any]]
    ) -> None:
        """
        在 conversation document 上更新 missing_fields 欄位，
        供前端與完成檢查使用。
        Input: Firestore conversationId, 欄位列表。
        """
        await self.conversations_col.document(conversation_id).update({
            "missing_fields": missing_fields,
            "updated_at": firestore.SERVER_TIMESTAMP
        })

    async def get_missing_fields(self, conversation_id: str) -> List[Dict[str, Any]]:
        """讀取最新 missing_fields 狀態，供完成檢查或 API 使用。"""
        doc = await self.conversations_col.document(conversation_id).get()
        if not doc.exists:
            return []
        data = doc.to_dict() or {}
        return data.get("missing_fields", [])

    async def get_current_specs(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """檢索當前會話的已提取規格"""
        doc = await self.conversations_col.document(
            conversation_id
        ).collection("extracted_specs").document(
            "current_version"
        ).get()

        return doc.to_dict() if doc.exists else None

    async def get_project_conversation(self, project_id: str) -> Optional[Dict[str, Any]]:
        """用 project_id 查找對話"""
        query = self.conversations_col.where("project_id", "==", project_id).limit(1)
        docs = query.stream()
        async for doc in docs:
            return doc.to_dict()
        return None

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """以 conversation_id 取得對話紀錄"""
        doc = await self.conversations_col.document(conversation_id).get()
        return doc.to_dict() if doc.exists else None

    async def project_exists(self, project_id: str) -> bool:
        """檢查專案是否存在"""
        doc = await self.db.collection("projects").document(project_id).get()
        return doc.exists

    async def create_project_in_db(self, project_id: str) -> None:
        """在 Firestore 中創建專案記錄"""
        await self.db.collection("projects").document(project_id).set({
            "id": project_id,
            "status": "created",
            "created_at": firestore.SERVER_TIMESTAMP,
        })

    async def log_event(
        self,
        conversation_id: str,
        event_type: str,
        *,
        severity: str = "info",
        source: str = "system",
        description: str = "",
        payload: Optional[Dict[str, Any]] = None
    ) -> None:
        """寫入對話事件日誌"""
        event_data = {
            "type": event_type,
            "severity": severity,
            "source": source,
            "description": description,
            "payload": payload or {},
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        try:
            await self.conversations_col.document(conversation_id).collection("events").add(event_data)
            await self.conversations_col.document(conversation_id).update({
                "last_event": event_type,
                "last_event_severity": severity,
                "updated_at": firestore.SERVER_TIMESTAMP
            })
        except Exception as exc:
            logger.warning(f"Failed to log event for conversation {conversation_id}: {exc}")

    async def get_events(
        self,
        conversation_id: str,
        *,
        limit: int = 50,
        severity: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """取得對話事件日誌"""
        events_ref = self.conversations_col.document(conversation_id).collection("events")
        query = events_ref

        if severity:
            query = query.where("severity", "==", severity)

        if since:
            if since.tzinfo is None:
                since = since.replace(tzinfo=timezone.utc)
            query = query.where("timestamp", ">=", since)

        query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()

        events: List[Dict[str, Any]] = []
        async for doc in docs:
            data = doc.to_dict() or {}
            data["id"] = doc.id
            events.append(data)
        return events
