"""
RAG API endpoints
Retrieval Augmented Generation for exercise advice and training guidance
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.rag_service import RAGService
from app.services.embedding_service import EmbeddingService
from app.services.pdf_service import PDFService
from app.constants import SAFETY_LEVELS, DEFAULT_SAFETY_LEVEL

router = APIRouter(prefix="/api/rag", tags=["rag"])


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Query text (1-1000 characters)")
    max_results: Optional[int] = Field(5, ge=1, le=20, description="Maximum number of results (1-20)")
    topics: Optional[List[str]] = Field(None, max_length=10, description="List of topics (max 10)")
    safety_level: Optional[str] = Field(DEFAULT_SAFETY_LEVEL, description=f"Safety level: {', '.join(SAFETY_LEVELS)}")

    @field_validator('safety_level')
    @classmethod
    def validate_safety_level(cls, v):
        if v not in SAFETY_LEVELS:
            raise ValueError(f"safety_level must be one of: {', '.join(SAFETY_LEVELS)}")
        return v

    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if not v or v.strip() == "":
            raise ValueError("query cannot be empty")
        return v.strip()


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
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Validate safety level
    if safety not in SAFETY_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid safety level. Must be one of: {', '.join(SAFETY_LEVELS)}"
        )

    try:
        # Read PDF content with size limit (10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )

        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
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
