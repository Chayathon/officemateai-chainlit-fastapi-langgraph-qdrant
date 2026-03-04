import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Load environment
load_dotenv()

# Configuration
EMBEDDING_URL = os.getenv("EMBEDDING_URL", "http://localhost:8081")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "dummy_token")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "officemate_knowledge")

# PDF Path
DATA_DIR = Path(__file__).parent.parent / "data"


def ingest_documents():
    """อ่าน PDF, หั่น Chunk, แปลง Vector, และบันทึกลง Qdrant"""
    
    print("=" * 60)
    print("🚀 OfficeMate AI - Document Ingestion")
    print("=" * 60)
    
    # 1. Find PDF files
    pdf_files = list(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ ไม่พบไฟล์ PDF ใน {DATA_DIR}")
        print("   กรุณาใส่ไฟล์ PDF เช่น employee_handbook.pdf")
        return
    
    print(f"\n📂 พบไฟล์ PDF {len(pdf_files)} ไฟล์:")
    for f in pdf_files:
        print(f"   - {f.name}")
    
    # 2. Load PDFs
    print("\n📖 กำลังอ่านไฟล์ PDF...")
    all_docs = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        # Add source metadata
        for doc in docs:
            doc.metadata["source"] = pdf_path.name
        all_docs.extend(docs)
        print(f"   ✅ {pdf_path.name}: {len(docs)} หน้า")
    
    print(f"\n   📄 รวมทั้งหมด: {len(all_docs)} หน้า")
    
    # 3. Split into chunks
    print("\n✂️ กำลังหั่นข้อความ (Chunking)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(all_docs)
    print(f"   ✅ ได้ทั้งหมด: {len(chunks)} chunks")
    
    # 4. Setup Embeddings
    print("\n🔌 กำลังเชื่อมต่อ Embedding Server...")
    embeddings = HuggingFaceEndpointEmbeddings(
        model=EMBEDDING_URL,
        huggingfacehub_api_token=EMBEDDING_API_KEY
    )
    
    # 5. Setup Qdrant
    print("\n🗄️ กำลังเชื่อมต่อ Qdrant...")
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY if QDRANT_API_KEY else None
    )
    
    # Delete existing collection
    if client.collection_exists(COLLECTION_NAME):
        print(f"   ⚠️ ลบ Collection เดิม '{COLLECTION_NAME}'...")
        client.delete_collection(COLLECTION_NAME)
    
    # Create new collection
    print(f"   📦 สร้าง Collection '{COLLECTION_NAME}'...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=1024,  # ขึ้นอยู่กับ Embedding Model
            distance=models.Distance.COSINE
        )
    )
    
    # 6. Embed and Store
    print("\n🚀 กำลังแปลงเป็น Vector และบันทึก...")
    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY if QDRANT_API_KEY else None,
        collection_name=COLLECTION_NAME
    )
    
    print(f"   ✅ บันทึกสำเร็จ!")
    
    # 7. Test search
    print("\n🔎 ทดสอบค้นหา...")
    test_query = "นโยบายการลา"
    results = vector_store.similarity_search(test_query, k=2)
    
    if results:
        print(f"   ✅ ค้นหา '{test_query}' พบ {len(results)} ผลลัพธ์")
        for i, doc in enumerate(results):
            print(f"\n   --- ผลลัพธ์ที่ {i+1} ---")
            print(f"   {doc.page_content[:150]}...")
    else:
        print("   ⚠️ ไม่พบผลลัพธ์")
    
    print("\n" + "=" * 60)
    print("✅ Ingestion เสร็จสมบูรณ์!")
    print("=" * 60)


if __name__ == "__main__":
    ingest_documents()