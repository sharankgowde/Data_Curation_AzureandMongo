from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from src.orchestrator import ingest_router

app = FastAPI(
    title="PDF RAG Chatbot API",
    description="Upload PDF documents, extract text, create embeddings, and store in MongoDB using Azure OpenAI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}
