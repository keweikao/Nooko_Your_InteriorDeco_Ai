from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import projects
from src.services.gemini_service import gemini_service
from datetime import datetime
import os

app = FastAPI(title="Interior Deco AI Partner - Analysis Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(projects.router, prefix="/api", tags=["projects"])

@app.get("/")
async def root():
    return {"message": "Analysis Service is running!"}

@app.get("/health")
async def health_check():
    """健康檢查端點,包含 Gemini API 狀態"""
    return {
        "status": "healthy",
        "gemini_enabled": gemini_service.enabled,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/debug/gemini-status")
async def gemini_status():
    """調試端點:檢查 Vertex AI Gemini 配置"""
    project_id = os.getenv("PROJECT_ID")
    vertex_location = os.getenv("VERTEX_LOCATION", "asia-east1")
    return {
        "project_id": project_id,
        "vertex_location": vertex_location,
        "gemini_enabled": gemini_service.enabled,
        "model": "gemini-1.5-flash" if gemini_service.enabled else None,
        "api_type": "Vertex AI"
    }
