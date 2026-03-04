from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.events import lifespan
from app.routers import chat
from app.services.qdrant import check_qdrant_health

# สร้าง FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Chatbot API สำหรับองค์กร - ตอบคำถามจากฐานความรู้",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router)


@app.get("/")
def root():
    """Health Check - Root Endpoint"""
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "🚀 OfficeMate AI is running!"
    }


@app.get("/health")
def health_check():
    """Detailed Health Check"""
    qdrant_health = check_qdrant_health()
    
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "qdrant": qdrant_health,
            "vllm": {"url": settings.VLLM_BASE_URL}
        }
    }