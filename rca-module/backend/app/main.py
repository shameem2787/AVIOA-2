from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.config import get_settings
from app.core.database import init_db
from app.routers import investigations

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Root Cause Analysis Module for Pharmaceutical Quality Systems",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(investigations.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "model": settings.GROQ_MODEL,
        "groq_configured": bool(settings.GROQ_API_KEY),
    }


@app.get("/")
def root():
    return {
        "message": "AIVOA RCA Module API",
        "docs": "/docs",
        "health": "/health",
    }
