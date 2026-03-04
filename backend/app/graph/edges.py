from app.graph.state import AgentState

def route_after_grade(state: AgentState) -> str:
    """ตัดสินใจว่าจะใช้ RAG หรือตอบตรงๆ"""
    if state.get("is_relevant", False):
        return "generate_rag"
    else:
        return "generate_direct"