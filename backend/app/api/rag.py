"""
RAG API endpoints
Retrieval Augmented Generation for exercise advice and training guidance
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.rag_service import RAGService
from app.services.embedding_service import EmbeddingService
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/api/rag", tags=["rag"])


class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    topics: Optional[List[str]] = None  # ["wrist", "shoulder", "training"]
    safety_level: Optional[str] = "general"  # "medical", "general", "training"


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float


class IngestResponse(BaseModel):
    document_id: int
    chunks_created: int
    message: str


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Query RAG system for exercise advice, training guidance, or injury prevention
    
    Example queries:
    - "How to improve wrist stability for aim training?"
    - "What exercises help with shoulder pain from gaming?"
    - "Best warm-up routine before KovaaK's sessions"
    """
    try:
        rag_service = RAGService(db)
        result = await rag_service.query(
            query=request.query,
            max_results=request.max_results,
            topics=request.topics,
            safety_level=request.safety_level
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@router.post("/ingest/pdf", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    doc_type: Optional[str] = "pdf",
    topics: Optional[List[str]] = None,
    safety: Optional[str] = "general",
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a PDF document into the RAG system
    
    Supported PDFs:
    - Aim training guides
    - Injury prevention articles
    - Exercise tutorials
    - Medical advice (with proper safety level)
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read PDF content
        content = await file.read()
        
        # Process PDF
        pdf_service = PDFService()
        chunks = await pdf_service.process_pdf(content)
        
        # Create document and chunks with embeddings
        rag_service = RAGService(db)
        result = await rag_service.ingest_document(
            title=title or file.filename,
            source=file.filename,
            doc_type=doc_type,
            topics=topics or [],
            safety=safety,
            chunks=chunks
        )
        
        return IngestResponse(
            document_id=result["document_id"],
            chunks_created=result["chunks_created"],
            message=f"Successfully ingested {file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF ingestion failed: {str(e)}")


@router.post("/ingest/text", response_model=IngestResponse)
async def ingest_text(
    title: str,
    content: str,
    doc_type: Optional[str] = "text",
    topics: Optional[List[str]] = None,
    safety: Optional[str] = "general",
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest plain text content into the RAG system
    
    Useful for:
    - Exercise descriptions
    - Training tips
    - Manual content entry
    """
    try:
        # Process text into chunks
        pdf_service = PDFService()
        chunks = await pdf_service.process_text(content)
        
        # Create document and chunks with embeddings
        rag_service = RAGService(db)
        result = await rag_service.ingest_document(
            title=title,
            source="manual_input",
            doc_type=doc_type,
            topics=topics or [],
            safety=safety,
            chunks=chunks
        )
        
        return IngestResponse(
            document_id=result["document_id"],
            chunks_created=result["chunks_created"],
            message=f"Successfully ingested text: {title}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text ingestion failed: {str(e)}")


@router.get("/documents")
async def list_documents(
    doc_type: Optional[str] = None,
    topics: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all ingested documents with optional filtering
    """
    try:
        rag_service = RAGService(db)
        documents = await rag_service.list_documents(
            doc_type=doc_type,
            topics=topics
        )
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a document and all its chunks
    """
    try:
        rag_service = RAGService(db)
        await rag_service.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Check RAG system health and embedding service status
    """
    try:
        embedding_service = EmbeddingService()
        is_healthy = await embedding_service.health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "embedding_service": "available" if is_healthy else "unavailable",
            "vector_dimension": 384  # FastEmbed bge-small
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
