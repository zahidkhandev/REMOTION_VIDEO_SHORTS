from google.cloud import texttospeech
from pathlib import Path
from mutagen.mp3 import MP3
from ..config import get_settings

settings = get_settings()


class TTSGenerator:
    def __init__(self):
        self.enabled = settings.enable_tts
        
        if self.enabled:
            try:
                self.client = texttospeech.TextToSpeechClient()
            except Exception as e:
                print(f"Warning: TTS client initialization failed: {e}")
                self.enabled = False
        
        self.audio_dir = settings.storage_path / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Remotion's public folder
        self.remotion_audio_dir = settings.remotion_project_path / "public" / "audio"
        self.remotion_audio_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_audio(
        self,
        script_id: str,
        scene_index: int,
        text: str,
        prompt: str = "Say the following in an engaging, enthusiastic way suitable for a short-form video.",
        voice_name: str = "Kore",  # Female voice, good for videos
        language_code: str = "en-US"
    ) -> tuple[str, float]:
        """
        Generate TTS audio using Gemini 2.5 Flash TTS.
        Returns: (relative_path, duration_seconds)
        """
        if not self.enabled:
            # Return estimated duration based on text length
            words = len(text.split())
            estimated_duration = max(2.0, words / 2.5)
            return "", estimated_duration
        
        # Use Gemini 2.5 Flash TTS
        synthesis_input = texttospeech.SynthesisInput(
            text=text,
            prompt=prompt  # Natural language style control!
        )
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            model_name="gemini-2.5-flash-tts"  # Latest Gemini TTS!
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            sample_rate_hertz=24000,  # High quality
        )
        
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Save to both locations
        audio_filename = f"{script_id}_scene_{scene_index}.mp3"
        
        # Backend storage
        backend_path = self.audio_dir / audio_filename
        backend_path.write_bytes(response.audio_content)
        
        # Remotion public folder
        remotion_path = self.remotion_audio_dir / audio_filename
        remotion_path.write_bytes(response.audio_content)
        
        # Get duration
        audio = MP3(str(backend_path))
        duration = audio.info.length
        
        # Return path relative to Remotion's public folder
        return f"audio/{audio_filename}", duration


# Singleton instance
tts_generator = TTSGenerator()
