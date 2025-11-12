from pathlib import Path
import json
from fastapi import UploadFile, HTTPException
from ..schemas.video import VideoScript, Scene
from ..core.gemini import gemini_analyzer
from ..core.tts import tts_generator
from ..core.pdf import pdf_extractor
from ..config import get_settings

settings = get_settings()

# Dynamic narration tone for TTS based on visual type
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
    """
    Full pipeline for PDF → Text → Gemini → (Optional TTS) → JSON props file.
    """

    def __init__(self):
        self.props_dir = settings.storage_path / "props"
        self.props_dir.mkdir(parents=True, exist_ok=True)

    async def process_paper(
        self,
        file: UploadFile,
        duration: int | None = None,
        skip_tts: bool = False,
        tts_type: str = "free"
    ) -> VideoScript:
        """Main video generation pipeline."""
        # Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

        filename = file.filename or "untitled"
        script_id = Path(filename).stem.replace(" ", "_").lower()

        print(f"📄 Processing paper '{filename}' (skip_tts={skip_tts}, tts_type={tts_type})")

        # Step 1: Extract text from PDF
        pdf_bytes = await file.read()
        paper_text = await pdf_extractor.extract_text(pdf_bytes)
        print(f"✅ Extracted {len(paper_text)} characters from PDF")

        # Step 2: Generate structured video script with Gemini
        target_duration = duration if duration is not None else settings.default_video_duration
        gemini_response = await gemini_analyzer.analyze_paper(paper_text, target_duration)

        # Step 3: Build VideoScript container
        video_script = VideoScript(
            script_id=script_id,
            scenes=[],
            total_duration_seconds=gemini_response.get("total_duration_seconds", target_duration),
        )

        total_calculated_duration = 0.0

        # Step 4: Process each Gemini scene
        for i, scene_data in enumerate(gemini_response.get("scenes", [])):
            try:
                visual_type = scene_data.get("visual", "explainer")

                # 4a: Handle TTS generation (only skip if explicitly requested)
                if skip_tts:
                    audio_path = ""
                    duration_sec = scene_data.get(
                        "duration_in_seconds",
                        max(2.0, len(scene_data["narration"].split()) / 2.5),
                    )
                    print(f"⏭️  Skipping TTS for scene {i}: Estimated {duration_sec:.1f}s")
                else:
                    tts_prompt = TTS_PROMPTS.get(visual_type, TTS_PROMPTS["explainer"])
                    print(f"🎙️  Generating TTS ({tts_type}) for scene {i}: {scene_data['title']}")
                    audio_path, duration_sec = await tts_generator.generate_audio(
                        script_id=script_id,
                        scene_index=i,
                        text=scene_data["narration"],
                        prompt=tts_prompt,
                        tts_type=tts_type
                    )

                # ✅ 4b: Preserve Gemini’s sound_effect
                sound_effect = scene_data.get("sound_effect")
                if not sound_effect:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Scene {i} missing sound_effect — Gemini returned none."
                    )

                # 4c: Create scene
                scene = Scene(
                    title=scene_data["title"],
                    narration=scene_data["narration"],
                    visual=visual_type,
                    audio_path=audio_path,
                    duration_in_seconds=duration_sec,
                    sound_effect=sound_effect,
                    visuals=scene_data["visuals"]
                )

                print(f"🎵 Scene {i} → {sound_effect}, duration: {duration_sec:.1f}s")
                video_script.scenes.append(scene)
                total_calculated_duration += duration_sec

            except Exception as e:
                print(f"❌ Failed to process scene {i}: {e}")
                raise HTTPException(status_code=500, detail=f"Error processing scene {i}: {e}")

        # Step 5: Validation
        if not video_script.scenes:
            raise HTTPException(status_code=500, detail="Failed to generate any scenes.")

        # Step 6: Update total duration
        video_script.total_duration_seconds = total_calculated_duration

        # Step 7: Save props JSON file
        props_path = self.props_dir / f"{script_id}.json"
        props_path.write_text(video_script.model_dump_json(indent=2), encoding="utf-8")

        print(f"✅ Saved: {props_path}")
        print(f"🎧 Final sound effects: {[s.sound_effect for s in video_script.scenes]}")
        print(f"🎬 Total duration: {video_script.total_duration_seconds:.1f}s")

        return video_script


# Singleton instance
paper_service = PaperService()
