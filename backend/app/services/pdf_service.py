"""
PDF Service - PDF processing and text chunking
"""
from typing import List, Dict, Any
import fitz  # PyMuPDF
import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    metadata: Dict[str, Any]


class PDFService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF service with chunking parameters

        Args:
            chunk_size: Size of each chunk in characters 
            chunk_overlap: Overlap between chunks to maintain context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def process_pdf(self, pdf_content: bytes) -> List[Dict[str, Any]]:
        """Extract text from PDF and chunk it"""
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            
            # Extract text from all pages
            full_text = ""
            page_metadata = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                full_text += f"\n\n--- Page {page_num + 1} ---\n\n{text}"
                
                page_metadata.append({
                    "page": page_num + 1,
                    "char_count": len(text)
                })
            
            doc.close()
            
            # Clean and chunk text
            cleaned_text = self._clean_text(full_text)
            chunks = self._chunk_text(cleaned_text)
            
            # Add metadata to chunks
            chunk_objects = []
            for i, chunk in enumerate(chunks):
                chunk_objects.append({
                    "content": chunk,
                    "metadata": {
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "source_type": "pdf",
                        "total_pages": len(page_metadata)
                    }
                })
            
            return chunk_objects
            
        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")
    
    async def process_text(self, text: str) -> List[Dict[str, Any]]:
        """Process plain text and chunk it"""
        cleaned_text = self._clean_text(text)
        chunks = self._chunk_text(cleaned_text)
        
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            chunk_objects.append({
                "content": chunk,
                "metadata": {
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                    "source_type": "text"
                }
            })
        
        return chunk_objects
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text.strip()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 chars
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + self.chunk_size - 100:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
