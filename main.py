# tldw_tube/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import summaries
import logging
from core.config import settings
import uvicorn
from database.database import engine  # Add import
from database import models  # Add import

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TL;DW Tube Backend",
    description="YouTube video summarization API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tldw.tube",
        "http://localhost:5173",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Function to initialize database schema (called before Gunicorn starts)
def init_db():
    """Initialize the database schema."""
    models.Base.metadata.create_all(bind=engine)

# Optional: Keep startup_even for other runtime initialization if needed
@app.on_event("startup")
def startup_event():
    """Handle startup events (e.g., logging or runtime initialization)."""
    logger.info("Application starting up...")

# Include the API router
app.include_router(summaries.router, prefix="/api")

@app.get("/api/health", response_model=dict)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level=settings.log_level.lower())

# For Docker: Call init_db() when run as a standalone script
if __name__ != "__main__":
    # This runs only in Docker via CMD, not when imported as a module
    init_db()