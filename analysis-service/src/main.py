from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import projects

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
