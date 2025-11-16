import asyncio
import logging
import os
from typing import Any, Dict, Optional

from src.models.project import Booking, Quote

try:
    from google.cloud import firestore
except ImportError:  # pragma: no cover - optional dependency for local dev
    firestore = None

logger = logging.getLogger(__name__)

FIRESTORE_COLLECTION = os.getenv("FIRESTORE_PROJECTS_COLLECTION", "projects")
DB_BACKEND = os.getenv("DB_BACKEND", "mock").lower()
DEFAULT_PROJECT_ID = (
    os.getenv("FIRESTORE_PROJECT_ID")
    or os.getenv("PROJECT_ID")
    or os.getenv("GCP_PROJECT")
    or os.getenv("GOOGLE_CLOUD_PROJECT")
)


class MockDBService:
    """In-memory database used for local development and testing."""

    def __init__(self) -> None:
        self._db: Dict[str, Dict] = {}

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        logger.info("MOCK DB: get project '%s'", project_id)
        return self._db.get(project_id)

    async def update_project(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("MOCK DB: update project '%s'", project_id)
        if project_id not in self._db:
            self._db[project_id] = {}

        self._db[project_id].update(data)
        logger.debug("MOCK DB: project '%s' data: %s", project_id, self._db[project_id])
        return self._db[project_id]

    async def update_project_with_quote(self, project_id: str, quote: Quote) -> None:
        await self.update_project(project_id, {"generated_quote": quote.model_dump()})

    async def update_project_with_rendering(self, project_id: str, rendering_url: str) -> None:
        await self.update_project(project_id, {"final_rendering_url": rendering_url})

    async def save_booking(self, booking: Booking) -> None:
        await self.update_project(
            booking.project_id,
            {
                "booking": booking.model_dump(),
                "status": "booked",
            },
        )


class FirestoreDBService:
    """Firestore-backed database service for production deployment."""

    def __init__(self, project_id: Optional[str] = None) -> None:
        if firestore is None:
            raise ImportError(
                "google-cloud-firestore is not installed. "
                "Install the dependency or switch DB_BACKEND to 'mock'."
            )

        # Allow Firestore to infer credentials from the environment
        self._client = firestore.Client(project=project_id)
        self._collection_name = FIRESTORE_COLLECTION

    def _project_ref(self, project_id: str):
        return self._client.collection(self._collection_name).document(project_id)

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        def _get_project() -> Optional[Dict[str, Any]]:
            doc = self._project_ref(project_id).get()
            return doc.to_dict() if doc.exists else None

        return await asyncio.to_thread(_get_project)

    async def update_project(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        def _update_project() -> Dict[str, Any]:
            doc_ref = self._project_ref(project_id)
            doc_ref.set(data, merge=True)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else data

        return await asyncio.to_thread(_update_project)

    async def update_project_with_quote(self, project_id: str, quote: Quote) -> None:
        await self.update_project(project_id, {"generated_quote": quote.model_dump()})

    async def update_project_with_rendering(self, project_id: str, rendering_url: str) -> None:
        await self.update_project(project_id, {"final_rendering_url": rendering_url})

    async def save_booking(self, booking: Booking) -> None:
        await self.update_project(
            booking.project_id,
            {
                "booking": booking.model_dump(),
                "status": "booked",
            },
        )


_db_service: Optional[Any] = None


def get_database_service() -> Any:
    global _db_service
    if _db_service is not None:
        return _db_service

    backend = DB_BACKEND.lower()
    if backend == "firestore":
        try:
            _db_service = FirestoreDBService(project_id=DEFAULT_PROJECT_ID)
            logger.info("Using FirestoreDBService for persistence.")
            return _db_service
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to initialize FirestoreDBService: %s", exc)
            logger.warning("Falling back to MockDBService.")

    _db_service = MockDBService()
    return _db_service


db_service = get_database_service()
# Backward compatibility for modules that previously imported mock_db_service
mock_db_service = db_service
