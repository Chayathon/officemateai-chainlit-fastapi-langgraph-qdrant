from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest, ChatResponse
from app.graph.workflow import agent_app

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint - ส่งคำถามและรับคำตอบ"""
    try:
        inputs = {
            "question": request.question,
            "context": None,
            "sources": [],
            "is_relevant": None,
            "answer": ""
        }
        
        print(f"📩 Question: {request.question}")
        result = await agent_app.ainvoke(inputs)
        
        return ChatResponse(
            answer=result["answer"],
            is_from_knowledge_base=result.get("is_relevant", False),
            sources=result.get("sources", [])
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Streaming Chat endpoint - ส่งคำตอบทีละ Token"""
    try:
        async def generate():
            inputs = {
                "question": request.question,
                "context": None,
                "sources": [],
                "is_relevant": None,
                "answer": ""
            }
            
            async for event in agent_app.astream_events(inputs, version="v1"):
                kind = event["event"]
                
                # เช็คว่า event นี้มาจาก Node ไหน
                # (ชื่อ node ต้องตรงกับที่คุณตั้งใน workflow.py เช่น 'generate_rag' หรือ 'generate_direct')
                node_name = event.get("metadata", {}).get("langgraph_node", "")
                
                # เงื่อนไข: ส่งข้อมูลเฉพาะเมื่อเป็น Node สร้างคำตอบเท่านั้น
                # (ไม่เอา output จาก grade_node หรือ retrieve_node)
                if kind == "on_chat_model_stream" and node_name in ["generate_rag", "generate_direct"]:
                    
                    content = event["data"]["chunk"].content
                    if content:
                        yield content
        
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))