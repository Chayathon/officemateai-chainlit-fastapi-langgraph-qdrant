from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from app.core.config import settings

class QdrantService:
    """Service สำหรับจัดการการเชื่อมต่อกับ Qdrant"""
    
    _client: QdrantClient = None
    _embeddings: HuggingFaceEndpointEmbeddings = None
    _vector_store: QdrantVectorStore = None
    
    @classmethod
    def get_client(cls) -> QdrantClient:
        """Get Qdrant Client"""
        if cls._client is None:
            cls._client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
            )
        return cls._client
    
    @classmethod
    def get_embeddings(cls) -> HuggingFaceEndpointEmbeddings:
        """Get Embedding Model"""
        if cls._embeddings is None:
            cls._embeddings = HuggingFaceEndpointEmbeddings(
                model=settings.EMBEDDING_URL,
                huggingfacehub_api_token=settings.EMBEDDING_API_KEY
            )
        return cls._embeddings
    
    @classmethod
    def get_vector_store(cls) -> QdrantVectorStore:
        """Get Vector Store"""
        if cls._vector_store is None:
            cls._vector_store = QdrantVectorStore(
                client=cls.get_client(),
                collection_name=settings.QDRANT_COLLECTION,
                embedding=cls.get_embeddings()
            )
        return cls._vector_store
    
    @classmethod
    def get_retriever(cls, k: int = 3):
        """Get Retriever สำหรับค้นหาเอกสาร"""
        return cls.get_vector_store().as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
    
    @classmethod
    def check_health(cls) -> dict:
        """ตรวจสอบสถานะการเชื่อมต่อ"""
        try:
            client = cls.get_client()
            collections = client.get_collections()
            collection_exists = any(
                c.name == settings.QDRANT_COLLECTION
                for c in collections.collections
            )
            return {
                "status": "connected",
                "collection_exists": collection_exists,
                "collection_name": settings.QDRANT_COLLECTION
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Shortcuts
def get_retriever(k: int = 3):
    return QdrantService.get_retriever(k)

def check_qdrant_health():
    return QdrantService.check_health()