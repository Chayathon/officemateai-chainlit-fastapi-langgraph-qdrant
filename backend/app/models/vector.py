from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class DocumentChunk(BaseModel):
    """Schema สำหรับ Document Chunk ที่จะเก็บใน Qdrant"""
    content: str = Field(..., description="เนื้อหาของ Chunk")
    metadata: Dict[str, Any] = Field(default={}, description="Metadata")
    
class SearchResult(BaseModel):
    """Schema สำหรับผลลัพธ์การค้นหา"""
    content: str
    score: float
    metadata: Dict[str, Any] = {}