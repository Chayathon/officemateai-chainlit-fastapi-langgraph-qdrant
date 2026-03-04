import os
import sys
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Supported file extensions
SUPPORTED_EXTENSIONS = [".pdf", ".csv", ".txt", ".docx"]

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


def load_file(file_path: Path) -> List[Document]:
    """
    โหลดไฟล์ตามนามสกุล และ return เป็น list ของ Document
    
    Args:
        file_path: Path ของไฟล์ที่ต้องการโหลด
        
    Returns:
        List[Document]: รายการ documents ที่โหลดได้
    """
    extension = file_path.suffix.lower()
    docs = []
    
    try:
        if extension == ".pdf":
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()
            
        elif extension == ".csv":
            loader = CSVLoader(
                file_path=str(file_path),
                encoding="utf-8"
            )
            docs = loader.load()
            
        elif extension == ".txt":
            loader = TextLoader(
                file_path=str(file_path),
                encoding="utf-8"
            )
            docs = loader.load()
            
        elif extension == ".docx":
            loader = Docx2txtLoader(str(file_path))
            docs = loader.load()
            
        else:
            print(f"   ⚠️ ไม่รองรับไฟล์ประเภท: {extension}")
            return []
            
    except Exception as e:
        print(f"   ❌ Error loading {file_path.name}: {e}")
        return []
    
    # Add source metadata
    for doc in docs:
        doc.metadata["source"] = file_path.name
        doc.metadata["file_type"] = extension
        
    return docs


def get_file_type_emoji(extension: str) -> str:
    """Return emoji ตามประเภทไฟล์"""
    emoji_map = {
        ".pdf": "📕",
        ".csv": "📊",
        ".txt": "📝",
        ".docx": "📘"
    }
    return emoji_map.get(extension, "📄")


def ingest_documents():
    """อ่านเอกสาร (PDF, CSV, TXT, DOCX), หั่น Chunk, แปลง Vector, และบันทึกลง Qdrant"""
    
    print("=" * 60)
    print("🚀 OfficeMate AI - Document Ingestion")
    print("=" * 60)
    print(f"📁 รองรับไฟล์: {', '.join(SUPPORTED_EXTENSIONS)}")
    
    # 1. Find all supported files
    all_files = []
    for ext in SUPPORTED_EXTENSIONS:
        all_files.extend(DATA_DIR.glob(f"*{ext}"))
    
    if not all_files:
        print(f"\n❌ ไม่พบไฟล์ใน {DATA_DIR}")
        print(f"   กรุณาใส่ไฟล์ประเภท: {', '.join(SUPPORTED_EXTENSIONS)}")
        return
    
    # Group files by type
    files_by_type = {}
    for f in all_files:
        ext = f.suffix.lower()
        if ext not in files_by_type:
            files_by_type[ext] = []
        files_by_type[ext].append(f)
    
    print(f"\n📂 พบไฟล์ทั้งหมด {len(all_files)} ไฟล์:")
    for ext, files in files_by_type.items():
        emoji = get_file_type_emoji(ext)
        print(f"\n   {emoji} {ext.upper()} ({len(files)} ไฟล์):")
        for f in files:
            print(f"      - {f.name}")
    
    # 2. Load all files
    print("\n📖 กำลังอ่านไฟล์...")
    all_docs = []
    for file_path in all_files:
        emoji = get_file_type_emoji(file_path.suffix.lower())
        docs = load_file(file_path)
        if docs:
            all_docs.extend(docs)
            # แสดงจำนวนตามประเภทไฟล์
            if file_path.suffix.lower() == ".pdf":
                print(f"   {emoji} {file_path.name}: {len(docs)} หน้า")
            elif file_path.suffix.lower() == ".csv":
                print(f"   {emoji} {file_path.name}: {len(docs)} แถว")
            else:
                print(f"   {emoji} {file_path.name}: {len(docs)} เอกสาร")
    
    print(f"\n   📄 รวมทั้งหมด: {len(all_docs)} เอกสาร")
    
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