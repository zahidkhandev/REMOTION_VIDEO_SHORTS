from fastapi import APIRouter, UploadFile, File, Query
from ..schemas.video import VideoScript
from ..services.paper_service import paper_service

router = APIRouter(prefix="/paper", tags=["paper"])


@router.post("/process", response_model=VideoScript)
async def process_paper(
    file: UploadFile = File(...),
    duration: int = Query(60, description="Target video duration in seconds"),
    skip_tts: bool = Query(False, description="Skip TTS generation (faster, no audio)")
):
    """
    Upload a PDF research paper and generate a structured video script.
    
    This endpoint:
    1. Extracts text from the PDF
    2. Analyzes it with Gemini to generate scenes
    3. (Optional) Creates TTS audio for each scene
    4. Returns the complete script with timing
    
    Set skip_tts=true to generate video without audio (much faster for testing).
    """
    return await paper_service.process_paper(file, duration, skip_tts)
