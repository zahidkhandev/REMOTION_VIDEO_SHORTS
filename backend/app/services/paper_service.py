from pathlib import Path
import json
from fastapi import UploadFile, HTTPException
from ..schemas.video import VideoScript, Scene
from ..core.gemini import gemini_analyzer
from ..core.tts import tts_generator
from ..core.pdf import pdf_extractor
from ..core.sound_effects import get_sound_effect
from ..config import get_settings

settings = get_settings()

# TTS prompts for each visual type
TTS_PROMPTS = {
    "title_card": "Say this with high energy and excitement, like a movie trailer announcement.",
    "explainer": "Explain this clearly and engagingly, as if teaching something fascinating.",
    "key_point": "Present these points with enthusiasm and emphasis on each one.",
    "quote": "Quote this thoughtfully and dramatically, as if it's profound.",
    "statistic": "Emphasize this statistic with surprise and impact.",
    "comparison": "Contrast these two things clearly and dramatically.",
    "timeline": "Narrate this as a step-by-step process with building momentum.",
    "conclusion": "Conclude with finality and impact, leaving the audience thinking."
}


class PaperService:
    def __init__(self):
        self.props_dir = settings.storage_path / "props"
        self.props_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_paper(
        self, 
        file: UploadFile, 
        duration: int | None = None,
        skip_tts: bool = False
    ) -> VideoScript:
        """
        Complete pipeline: PDF -> Text -> Gemini -> (Optional TTS) -> JSON props
        """
        # Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a PDF."
            )
        
        # Generate script ID from filename
        filename = file.filename or "untitled"
        script_id = Path(filename).stem.replace(" ", "_").lower()
        
        # Step 1: Extract PDF text
        pdf_bytes = await file.read()
        paper_text = await pdf_extractor.extract_text(pdf_bytes)
        
        # Step 2: Analyze with Gemini
        target_duration = duration if duration is not None else settings.default_video_duration
        gemini_response = await gemini_analyzer.analyze_paper(paper_text, target_duration)
        
        # Step 3: Generate TTS for each scene (or skip if disabled)
        video_script = VideoScript(script_id=script_id, scenes=[])
        
        for i, scene_data in enumerate(gemini_response.get("scenes", [])):
            try:
                visual_type = scene_data.get("visual", "explainer")
                
                if skip_tts or not settings.enable_tts:
                    # Skip TTS generation
                    audio_path = ""
                    # Estimate duration based on narration length
                    words = len(scene_data["narration"].split())
                    duration_sec = max(2.0, words / 2.5)
                else:
                    # Get TTS prompt for this visual type
                    tts_prompt = TTS_PROMPTS.get(visual_type, TTS_PROMPTS["explainer"])
                    
                    # Generate audio with Gemini 2.5 Flash TTS
                    audio_path, duration_sec = await tts_generator.generate_audio(
                        script_id=script_id,
                        scene_index=i,
                        text=scene_data["narration"],
                        prompt=tts_prompt  # Dynamic prompt!
                    )
                
                # Get sound effect for this visual type
                sound_effect = get_sound_effect(visual_type)
                
                # Create scene with audio metadata and sound effects
                scene = Scene(
                    title=scene_data["title"],
                    narration=scene_data["narration"],
                    visual=visual_type,
                    audio_path=audio_path,
                    duration_in_seconds=duration_sec,
                    sound_effect=sound_effect
                )
                
                video_script.scenes.append(scene)
                video_script.total_duration_seconds += duration_sec
                
            except Exception as e:
                print(f"Failed to process scene {i}: {e}")
                continue
        
        if not video_script.scenes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate any scenes. Please try again."
            )
        
        # Step 4: Save props JSON
        props_path = self.props_dir / f"{script_id}.json"
        props_path.write_text(
            video_script.model_dump_json(indent=2),
            encoding="utf-8"
        )
        
        return video_script


# Singleton instance
paper_service = PaperService()
