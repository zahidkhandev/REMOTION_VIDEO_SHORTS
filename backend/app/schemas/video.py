from pydantic import BaseModel, Field
from typing import Literal, Optional, List


class SVGElement(BaseModel):
    """AI-generated SVG element"""
    type: str
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
    """A single scene in the generated video script"""
    title: str
    narration: str
    visual: str
    audio_path: Optional[str] = None
    duration_in_seconds: float
    sound_effect: str = Field(..., description="Sound effect identifier from Gemini or fallback")  # ✅ required
    visuals: SceneVisuals  # AI-generated SVG scene visuals


class VideoScript(BaseModel):
    """Full generated video script"""
    script_id: str
    scenes: List[Scene]
    total_duration_seconds: float


class RenderRequest(BaseModel):
    """Request body for the /video/render endpoint"""
    script_id: str


class RenderResponse(BaseModel):
    """Response body for the /video/render endpoint"""
    video_url: str
    script_id: str
