from app.graph.state import AgentState
from app.services.llm import get_llm
from app.services.qdrant import get_retriever
from langchain_core.prompts import ChatPromptTemplate

# --- Node 1: Retrieve ---
def retrieve_node(state: AgentState) -> dict:
    """ค้นหาเอกสารที่เกี่ยวข้องจาก Qdrant"""
    print("🔍 [Retrieve] กำลังค้นหาเอกสาร...")
    
    question = state["question"]
    retriever = get_retriever(k=3)
    
    try:
        docs = retriever.invoke(question)
        
        if docs:
            context = "\n\n---\n\n".join([doc.page_content for doc in docs])
            sources = [doc.metadata.get("source", "unknown") for doc in docs]
            print(f"   ✅ พบเอกสาร {len(docs)} รายการ")
            return {"context": context, "sources": sources}
        else:
            print("   ⚠️ ไม่พบเอกสาร")
            return {"context": "", "sources": []}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"context": "", "sources": []}


# --- Node 2: Grade ---
def grade_node(state: AgentState) -> dict:
    """ตรวจสอบว่า context เกี่ยวข้องกับคำถามหรือไม่"""
    print("📝 [Grade] กำลังตรวจสอบความเกี่ยวข้อง...")
    
    question = state["question"]
    context = state.get("context", "")
    
    if not context:
        print("   ❌ ไม่มี context")
        return {"is_relevant": False}
    
    llm = get_llm()
    
    grade_prompt = ChatPromptTemplate.from_messages([
        ("system", """คุณเป็นผู้ตรวจสอบความเกี่ยวข้องของเอกสาร
ตอบว่า "YES" ถ้าเอกสารมีข้อมูลที่ช่วยตอบคำถามได้
ตอบว่า "NO" ถ้าเอกสารไม่เกี่ยวข้องกับคำถาม
ตอบแค่ YES หรือ NO เท่านั้น"""),
        ("human", """คำถาม: {question}

เอกสาร:
{context}

เอกสารนี้เกี่ยวข้องกับคำถามหรือไม่?""")
    ])
    
    chain = grade_prompt | llm
    result = chain.invoke({"question": question, "context": context})
    
    is_relevant = "YES" in result.content.upper()
    print(f"   {'✅ เกี่ยวข้อง' if is_relevant else '❌ ไม่เกี่ยวข้อง'}")
    
    return {"is_relevant": is_relevant}


# --- Node 3: Generate RAG ---
def generate_rag_node(state: AgentState) -> dict:
    """สร้างคำตอบจาก context (RAG)"""
    print("🤖 [Generate RAG] กำลังสร้างคำตอบจากเอกสาร...")
    
    question = state["question"]
    context = state.get("context", "")
    
    llm = get_llm()
    
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", """คุณเป็น OfficeMate AI ผู้ช่วยตอบคำถามเกี่ยวกับองค์กร
- ตอบคำถามโดยอ้างอิงจากเอกสารที่ให้มาเท่านั้น
- ถ้าไม่มีข้อมูลในเอกสาร ให้บอกตรงๆ ว่าไม่พบข้อมูล
- ตอบเป็นภาษาไทย กระชับ ได้ใจความ
- ใช้ภาษาสุภาพ เป็นมิตร
- **ห้าม** ขึ้นต้นคำตอบด้วยคำว่า "YES", "NO", "Based on", หรือทวนคำถาม ให้ตอบเนื้อหาทันที"""), # <--- เพิ่มบรรทัดนี้
        ("human", """เอกสารอ้างอิง:
{context}

คำถาม: {question}

คำตอบ:""")
    ])
    
    chain = rag_prompt | llm
    result = chain.invoke({"question": question, "context": context})
    
    return {"answer": result.content}


# --- Node 4: Generate Direct ---
def generate_direct_node(state: AgentState) -> dict:
    """สร้างคำตอบแบบทั่วไป (ไม่ใช้ RAG)"""
    print("💬 [Generate Direct] กำลังตอบคำถามทั่วไป...")
    
    question = state["question"]
    
    llm = get_llm()
    
    direct_prompt = ChatPromptTemplate.from_messages([
        ("system", """คุณเป็น OfficeMate AI ผู้ช่วยในองค์กร
- ตอบคำถามทั่วไปได้อย่างเป็นมิตร
- ถ้าเป็นคำถามเกี่ยวกับนโยบายหรือข้อมูลองค์กร ให้แนะนำว่าไม่พบข้อมูลในฐานความรู้
- ตอบเป็นภาษาไทย สุภาพ กระชับ"""),
        ("human", "{question}")
    ])
    
    chain = direct_prompt | llm
    result = chain.invoke({"question": question})
    
    return {"answer": result.content}