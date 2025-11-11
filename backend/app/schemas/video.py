from pydantic import BaseModel
from typing import Literal, Optional, List


class SVGElement(BaseModel):
    """AI-generated SVG element"""
    type: Literal["path", "circle", "rect", "line", "text", "equation"]
    data: str  # SVG path data, radius, dimensions, or text content
    x: float
    y: float
    color: str
    stroke_width: float = 3
    animation: Literal["draw", "fade", "scale", "morph", "pulse"] = "draw"
    delay: float = 0  # Animation delay in frames


class SceneVisuals(BaseModel):
    """Complete visual description for a scene"""
    svg_elements: List[SVGElement]
    background_color: str = "#0a0e27"
    particles: bool = False
    grid: bool = True


class Scene(BaseModel):
    title: str
    narration: str
    visual: Literal[
        "title_card",
        "explainer",
        "key_point",
        "quote",
        "statistic",
        "comparison",
        "timeline",
        "conclusion"
    ]
    audio_path: Optional[str] = None
    duration_in_seconds: float
    sound_effect: str
    visuals: SceneVisuals  # NEW: AI-generated SVG scene


class VideoScript(BaseModel):
    script_id: str
    scenes: List[Scene]
    total_duration_seconds: float


# --- FIX: ADD THESE MISSING MODELS ---

class RenderRequest(BaseModel):
    """Request body for the /video/render endpoint"""
    script_id: str


class RenderResponse(BaseModel):
    """Response body for the /video/render endpoint"""
    video_url: str
    script_id: str