from fastapi import APIRouter, UploadFile, File, Query
from ..schemas.video import VideoScript
from ..services.paper_service import paper_service

router = APIRouter(prefix="/paper", tags=["paper"])


@router.post("/process", response_model=VideoScript)
async def process_paper(
    file: UploadFile = File(...),
    duration: int = Query(60, description="Target video duration in seconds"),
    skip_tts: bool = Query(True, description="Skip TTS generation (faster, no audio)"),
    tts_type: str = Query("free", description="TTS engine: 'free', 'google', or 'gemini'")
):
    """
    Upload a PDF research paper and generate a structured video script.

    This endpoint:
    1. Extracts text from the PDF
    2. Analyzes it with Gemini to generate scenes
    3. (Optional) Creates TTS audio for each scene
    4. Returns the complete script with timing and visuals

    Parameters:
    - skip_tts: If True, skips generating audio (faster)
    - tts_type: Selects which TTS engine to use ('free', 'google', 'gemini')
    """
    return await paper_service.process_paper(file, duration, skip_tts, tts_type)
