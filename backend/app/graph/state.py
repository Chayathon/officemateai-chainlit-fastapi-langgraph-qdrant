from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    """State สำหรับ LangGraph Agent"""
    
    # Input
    question: str                           # คำถามจากผู้ใช้
    
    # RAG Data
    context: Optional[str]                  # เอกสารที่ค้นเจอ
    sources: List[str]                      # แหล่งอ้างอิง
    
    # Decision
    is_relevant: Optional[bool]             # context เกี่ยวข้องไหม
    
    # Output
    answer: str                             # คำตอบสุดท้าย