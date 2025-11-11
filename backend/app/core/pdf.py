import fitz  # PyMuPDF
from fastapi import HTTPException


class PDFExtractor:
    @staticmethod
    async def extract_text(pdf_bytes: bytes) -> str:
        """Extract text content from PDF."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            
            for page in doc:
                page_text = page.get_text()  # Fixed: get_text() returns str
                if isinstance(page_text, str):
                    text += page_text
            
            doc.close()
            
            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="PDF appears to be empty or contains only images."
                )
            
            return text
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )


# Singleton instance
pdf_extractor = PDFExtractor()
