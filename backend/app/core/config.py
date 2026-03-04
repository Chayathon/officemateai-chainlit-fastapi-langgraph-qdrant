import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# คำนวณหาตำแหน่ง Root ของโปรเจกต์ (ถอยหลังกลับไป 3 ชั้นจากไฟล์นี้)
# ไฟล์นี้อยู่: backend/app/core/config.py
# .parent -> backend/app/core
# .parent.parent -> backend/app
# .parent.parent.parent -> backend
# .parent.parent.parent.parent -> 06-officemate-ai-workshop (Root ที่มี .env)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    """Application Settings - โหลดจาก Environment Variables"""
    
    # Application
    APP_NAME: str = "OfficeMate AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # vLLM
    VLLM_BASE_URL: str = "http://localhost:8001/v1"
    VLLM_API_KEY: str = "EMPTY"
    VLLM_MODEL_NAME: str = "Qwen/Qwen2.5-14B-Instruct-AWQ"
    
    # Embedding
    EMBEDDING_URL: str = "http://localhost:8081"
    EMBEDDING_API_KEY: str = "dummy_token"
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "officemate_knowledge"
    
    # การตั้งค่า Config แบบใหม่ (Pydantic v2)
    model_config = SettingsConfigDict(
        # ให้มองหา .env ที่ Root Project เสมอ
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        # ถ้าหาไฟล์ไม่เจอ ให้ข้ามไป (ไม่ Error) ไปใช้ System Env หรือ Default แทน
        extra="ignore" 
    )

    # แบบเดิม (Legacy Pydantic v1) ถ้าคุณยังไม่อยากเปลี่ยน
    # class Config:
    #     env_file = os.path.join(BASE_DIR, ".env")
    #     env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Singleton Pattern สำหรับ Settings"""
    return Settings()

# Shortcut สำหรับเรียกใช้งาน
settings = get_settings()