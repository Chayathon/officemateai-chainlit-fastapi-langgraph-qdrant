from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events สำหรับ FastAPI"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📡 vLLM: {settings.VLLM_BASE_URL}")
    print(f"🗄️ Qdrant: {settings.QDRANT_URL}")
    
    yield
    
    # Shutdown
    print(f"👋 Shutting down {settings.APP_NAME}")