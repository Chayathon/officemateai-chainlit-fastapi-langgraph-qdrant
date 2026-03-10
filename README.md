# 🚀 OfficeMate AI

ระบบ AI Chatbot สำหรับองค์กรที่ช่วยตอบคำถามเกี่ยวกับนโยบาย สวัสดิการ สินค้า และข้อมูลอื่นๆ จากฐานความรู้ขององค์กร โดยใช้ RAG (Retrieval-Augmented Generation) ร่วมกับ LLM (Large Language Model)

## 📋 รายละเอียดโปรเจค

OfficeMate AI เป็นระบบตอบคำถาม AI ขั้นสูงที่สามารถ:

- 🎯 ตอบคำถามจากฐานความรู้ขององค์กร
- ⚡ ประมวลผลด้วย LLM ที่ทรงพลัง (Qwen3)
- 🔍 ค้นหาเอกสารจาก Vector Database (Qdrant)
- 💬 โต้ตอบผ่าน Chainlit UI ที่สวยงาม
- 📊 ติดตามแหล่งข้อมูลของคำตอบ

## 🏗️ สถาปัตยกรรม

```
┌─────────────────────────────────────────────┐
│        Frontend (Chainlit)                  │
│   - Chat UI สำหรับผู้ใช้                         │
└──────────────┬──────────────────────────────┘
               │ HTTP/WebSocket
┌──────────────▼──────────────────────────────┐
│        Backend (FastAPI)                    │
│   - API Endpoints                           │
│   - RAG Workflow (LangGraph)                │
└──┬─────────────┬─────────────┬──────────────┘
   │             │             │
   ▼             ▼             ▼
┌──────┐  ┌──────────────┐  ┌──────────┐
│vLLM  │  │ Text Embed   │  │ Qdrant   │
│(LLM) │  │ (BGE-M3)     │  │ (Vector) │
└──────┘  └──────────────┘  └──────────┘
```

## 🛠️ Tech Stack

### Frontend

- **Chainlit** - UI Component Library สำหรับ Chat Interface

### Backend

- **FastAPI** - Backend API Framework
- **LangGraph** - Workflow Orchestration & Graph-based Processing
- **LangChain** - LLM Integration & RAG Framework

### LLM & Embeddings

- **vLLM + Qwen2.5-14B** - LLM Serving Engine พร้อมโมเดล Quantized
- **Text Embeddings Inference (BGE-M3)** - Embedding Model Service

### Database

- **Qdrant** - Vector Database สำหรับ RAG

### Infrastructure

- **Docker & Docker Compose** - Container Orchestration

## 🚀 Quick Start

### ข้อกำหนดเบื้องต้น

- Docker & Docker Compose
- NVIDIA GPU (สำหรับ vLLM)
- Python 3.13+ (สำหรับ Local Development)
- HuggingFace Token (สำหรับ Model Access)

### Installation & Setup

#### 1. Clone Repository

```bash
git clone <repository-url>
cd officemate-ai-chainlit-fastapi-langgraph-qdrant
```

#### 2. สร้างไฟล์ .env

```bash
cp .env.example .env
```

จากนั้นแก้ไขค่าต่อไปนี้:

```env
# LLM Configuration
VLLM_BASE_URL=http://vllm:8000/v1
VLLM_API_KEY=EMPTY
VLLM_MODEL_NAME=Qwen/Qwen2.5-14B-Instruct-AWQ

# Embedding Configuration
EMBEDDING_URL=http://embeddings:8081
EMBEDDING_API_KEY=dummy_token

# Qdrant Configuration
QDRANT_URL=http://qdrant:6333

# API Configuration
API_BASE_URL=http://localhost:8000

# HuggingFace Token
HUGGING_FACE_HUB_TOKEN=<your_huggingface_token>
```

#### 3. เตรียมข้อมูล

ใส่ไฟล์เอกสารของคุณลงใน `data/` folder:

- `.txt` - ไฟล์ข้อความ
- `.pdf` - ไฟล์ PDF
- `.csv` - ไฟล์ CSV

#### 4. รัน Docker Compose

```bash
# สร้างและรัน Services
docker-compose up -d

# ตรวจสอบ Status
docker-compose ps
```

#### 5. Ingest Data

```bash
# Backend Environment
cd backend

# Ingest ทั้งหมด
python scripts/ingest_all.py

# หรือ Ingest ไฟล์เฉพาะ
python scripts/ingest.py --file data/sample_product.csv
```

#### 6. เปิด Application

- **Frontend (Chainlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## 📁 โครงสร้างโปรเจกต์

```
officemate-ai-chainlit-fastapi-langgraph-qdrant/
├── backend/                      # Backend FastAPI
│   ├── app/
│   │   ├── main.py              # FastAPI Application
│   │   ├── core/
│   │   │   ├── config.py        # Configuration Settings
│   │   │   └── events.py        # Startup/Shutdown Events
│   │   ├── graph/
│   │   │   ├── workflow.py      # RAG Workflow (LangGraph)
│   │   │   ├── nodes.py         # Graph Nodes
│   │   │   ├── edges.py         # Graph Edges
│   │   │   └── state.py         # Agent State Schema
│   │   ├── models/
│   │   │   ├── chat.py          # Chat Request/Response
│   │   │   └── vector.py        # Vector-related Models
│   │   ├── routers/
│   │   │   └── chat.py          # Chat API Routes
│   │   └── services/
│   │       ├── llm.py           # LLM Service
│   │       └── qdrant.py        # Qdrant Service
│   ├── Dockerfile               # Docker Image
│   └── requirements.txt          # Python Dependencies
│
├── frontend/                     # Frontend Chainlit
│   ├── app.py                   # Chainlit Application
│   ├── chainlit.md              # Chainlit Welcome Message
│   ├── Dockerfile               # Docker Image
│   └── requirements.txt          # Python Dependencies
│
├── data/                        # ข้อมูล & Knowledge Base
│   ├── sample_product.csv       # ตัวอย่างข้อมูลสินค้า
│   └── shop_info.txt            # ข้อมูลบริษัท
│
├── scripts/                     # Utility Scripts
│   ├── ingest_all.py           # Ingest ทั้งหมด
│   └── ingest.py               # Ingest ไฟล์เฉพาะ
│
├── docker-compose.yml           # Docker Compose Configuration
├── pyproject.toml              # Project Dependencies (uv)
├── .env.example                # Environment Example
└── README.md                   # Documentation
```

## 🔄 RAG Workflow

ระบบใช้ Graph-based Architecture สำหรับการประมวลผล:

```
User Question
     │
     ▼
┌─────────────────────────────┐
│  1. RETRIEVE                │  ค้นหาเอกสารจาก Qdrant
│     (retrieve_node)         │  ที่เกี่ยวข้องกับคำถาม
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  2. GRADE                   │  ประเมินความเกี่ยวข้อง
│     (grade_node)            │  ของเอกสารที่ค้นหาได้
└──┬────────────────┬─────────┘
   │                │
   │ Relevant       │ Not Relevant
   ▼                ▼
┌──────────────┐ ┌──────────────────┐
│ 3a. GEN RAG  │ │ 3b. GEN DIRECT   │
│ Use Context  │ │ Use Knowledge    │
│ from Docs    │ │ Only             │
└──────┬───────┘ └────────┬─────────┘
       │                  │
       └────┬─────────────┘
            ▼
         Answer
```

### Graph Nodes

1. **retrieve_node**: ค้นหาเอกสารจาก Vector DB โดยใช้ Embeddings
2. **grade_node**: ประเมินว่าเอกสารที่ค้นหาได้มีความเกี่ยวข้องหรือไม่
3. **generate_rag_node**: สร้างคำตอบจากเอกสารที่เกี่ยวข้อง
4. **generate_direct_node**: สร้างคำตอบจากความรู้โดยตรงของ LLM

## 🔌 API Endpoints

### Chat Endpoints

#### `POST /chat`

ส่งคำถามและรับคำตอบแบบทั่วไป

**Request:**

```json
{
    "question": "นโยบายการลาป่วยเป็นอย่างไร?"
}
```

**Response:**

```json
{
    "answer": "ตามนโยบายบริษัท...",
    "is_from_knowledge_base": true,
    "sources": ["shop_info.txt", "policy.pdf"]
}
```

#### `POST /chat/stream`

ส่งคำถามและรับคำตอบแบบ Streaming (Token by Token)

### Health Check

#### `GET /`

```json
{
    "status": "ok",
    "app_name": "OfficeMate AI",
    "version": "1.0.0",
    "message": "🚀 OfficeMate AI is running!"
}
```

#### `GET /health`

ตรวจสอบสถานะของบริการทั้งหมด

```json
{
    "status": "ok",
    "app_name": "OfficeMate AI",
    "version": "1.0.0",
    "services": {
        "qdrant": "connected"
    }
}
```

## 🛠️ Development

### Local Setup

```bash
# สร้าง Virtual Environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install Dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### รัน Backend (Development)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### รัน Frontend (Development)

```bash
cd frontend
chainlit run app.py
```

## 🧪 Testing

```bash
# Run Backend Tests
pytest backend/tests/

# Run with Coverage
pytest backend/tests/ --cov=app --cov-report=html
```

## 🐳 Docker Commands

```bash
# Build Images
docker-compose build

# Start Services
docker-compose up -d

# View Logs
docker-compose logs -f

# Stop Services
docker-compose down

# Remove All Data
docker-compose down -v
```

## 📊 Monitoring

### Qdrant Dashboard

เข้าถึงได้ที่: http://localhost:6333/dashboard

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Logs

```bash
# Backend Logs
docker-compose logs -f backend

# Frontend Logs
docker-compose logs -f frontend

# All Services
docker-compose logs -f
```

## 📚 References

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Chainlit Documentation](https://docs.chainlit.io/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [vLLM Documentation](https://docs.vllm.ai/)
