from fastapi import APIRouter
from ..schemas.video import RenderRequest, RenderResponse
from ..services.video_service import video_service

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/render", response_model=RenderResponse)
async def render_video(request: RenderRequest):
    """
    Render a video from a processed paper script using Remotion.
    
    This is a long-running operation (1-5 minutes depending on duration).
    In production, this should be moved to a background job queue.
    """
    video_url = await video_service.render_video(request.script_id)
    return RenderResponse(video_url=video_url, script_id=request.script_id)
