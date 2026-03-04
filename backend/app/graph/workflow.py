from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes import (
    retrieve_node,
    grade_node,
    generate_rag_node,
    generate_direct_node
)
from app.graph.edges import route_after_grade

def create_rag_workflow():
    """สร้าง RAG Workflow Graph"""
    
    # สร้าง Graph
    workflow = StateGraph(AgentState)
    
    # เพิ่ม Nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade", grade_node)
    workflow.add_node("generate_rag", generate_rag_node)
    workflow.add_node("generate_direct", generate_direct_node)
    
    # กำหนดจุดเริ่มต้น
    workflow.set_entry_point("retrieve")
    
    # เชื่อม Edges
    workflow.add_edge("retrieve", "grade")
    
    # Conditional Edge
    workflow.add_conditional_edges(
        "grade",
        route_after_grade,
        {
            "generate_rag": "generate_rag",
            "generate_direct": "generate_direct"
        }
    )
    
    # End
    workflow.add_edge("generate_rag", END)
    workflow.add_edge("generate_direct", END)
    
    return workflow.compile()


# สร้าง Instance สำหรับใช้งาน
agent_app = create_rag_workflow()