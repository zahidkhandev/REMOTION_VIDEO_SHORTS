from pydantic import BaseModel, Field
from typing import List, Literal


class Scene(BaseModel):
    title: str = Field(..., description="Scene title or key point")
    narration: str = Field(..., description="Narration text for TTS")
    visual: Literal[
        "title_card", 
        "explainer", 
        "key_point", 
        "quote", 
        "statistic",
        "comparison",
        "timeline",
        "conclusion"
    ] = Field(..., description="Visual style hint for Remotion")
    audio_path: str | None = Field(None, description="Relative path to audio file")
    duration_in_seconds: float = Field(0.0, description="Audio duration")
    sound_effect: str = Field("soft_ambient", description="Sound effect type for Remotion")


class VideoScript(BaseModel):
    script_id: str
    scenes: List[Scene]
    total_duration_seconds: float = 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "script_id": "sample_paper",
                "scenes": [
                    {
                        "title": "Revolutionary AI Discovery",
                        "narration": "Scientists have unveiled a breakthrough.",
                        "visual": "title_card",
                        "audio_path": "",
                        "duration_in_seconds": 3.5,
                        "sound_effect": "whoosh_impact"
                    }
                ],
                "total_duration_seconds": 3.5
            }
        }


class RenderRequest(BaseModel):
    script_id: str


class RenderResponse(BaseModel):
    video_url: str
    script_id: str
