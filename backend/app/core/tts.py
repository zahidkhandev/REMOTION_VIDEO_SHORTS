import aiohttp
from pathlib import Path
from mutagen.mp3 import MP3
from google.cloud import texttospeech
import google.generativeai as genai
from ..config import get_settings

settings = get_settings()


class TTSGenerator:
    """
    Text-to-Speech Generator supporting:
    1. Free Google Translate TTS (default, via CNTLM proxy)
    2. Google Cloud TTS (paid, neural quality)
    3. Gemini TTS (if explicitly selected + API key provided)
    """

    def __init__(self):
        self.audio_dir = settings.storage_path / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        self.remotion_audio_dir = settings.remotion_project_path / "public" / "audio"
        self.remotion_audio_dir.mkdir(parents=True, exist_ok=True)

        # CNTLM proxy config — adjust if needed
        self.proxy_url = "http://127.0.0.1:8080"

    async def generate_audio(
        self,
        script_id: str,
        scene_index: int,
        text: str,
        tts_type: str = "free",  # "free", "google", or "gemini"
        prompt: str = "Say this in an engaging, enthusiastic way suitable for a short-form video.",
        voice_name: str = "en-US-Neural2-F",
        language_code: str = "en-US",
    ) -> tuple[str, float]:
        """Generate TTS audio using the selected engine, with CNTLM proxy and fallbacks."""
        tts_type = tts_type.lower().strip()
        audio_filename = f"{script_id}_scene_{scene_index}.mp3"
        backend_path = self.audio_dir / audio_filename
        remotion_path = self.remotion_audio_dir / audio_filename

        try:
            if tts_type in ("free", "translate", "default"):
                await self._generate_translate_tts(text, language_code, backend_path)
            elif tts_type == "google":
                await self._generate_google_tts(text, prompt, voice_name, language_code, backend_path)
            elif tts_type == "gemini":
                if not settings.gemini_api_key:
                    raise Exception("Gemini API key not found — cannot use Gemini TTS.")
                await self._generate_gemini_tts(text, prompt, backend_path)
            else:
                raise ValueError(f"Unsupported tts_type: {tts_type}")

            # Copy to Remotion's public folder
            remotion_path.write_bytes(backend_path.read_bytes())

            # Detect duration
            audio = MP3(str(backend_path))
            duration = audio.info.length
            print(f"✅ TTS success ({tts_type}) → {backend_path.name}")
            return f"audio/{audio_filename}", duration

        except Exception as e:
            print(f"❌ TTS generation failed ({tts_type}): {e}")

            # 🔄 Try fallback to Google Cloud if free TTS fails
            if tts_type in ("free", "translate", "default"):
                try:
                    print("⚙️ Falling back to Google Cloud TTS...")
                    await self._generate_google_tts(text, prompt, voice_name, language_code, backend_path)
                    remotion_path.write_bytes(backend_path.read_bytes())
                    audio = MP3(str(backend_path))
                    duration = audio.info.length
                    print(f"✅ Google Cloud fallback success → {backend_path.name}")
                    return f"audio/{audio_filename}", duration
                except Exception as inner_e:
                    print(f"❌ Google Cloud fallback also failed: {inner_e}")

            # 🕒 Last resort: estimate duration
            words = len(text.split())
            estimated_duration = max(2.0, words / 2.5)
            return "", estimated_duration

    # ------------------------------
    # INDIVIDUAL ENGINE IMPLEMENTATIONS
    # ------------------------------

    async def _generate_translate_tts(self, text: str, language_code: str, backend_path: Path):
        """
        Free Google Translate TTS (female-sounding, no API key).
        CNTLM-aware — routes through proxy http://127.0.0.1:8080.
        """
        print(f"🌐 Using free Google Translate TTS via CNTLM proxy ({self.proxy_url})...")
        url = "https://translate.google.com/translate_tts"
        params = {
            "ie": "UTF-8",
            "q": text,
            "tl": language_code,
            "client": "tw-ob",
        }

        connector = aiohttp.TCPConnector(ssl=False)  # disable strict SSL (CNTLM handles upstream TLS)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, params=params, proxy=self.proxy_url) as response:
                if response.status != 200:
                    raise Exception(f"Translate TTS failed with HTTP {response.status}")
                audio_data = await response.read()

        backend_path.write_bytes(audio_data)
        print(f"🔊 Translate TTS generated → {backend_path.name}")

    async def _generate_google_tts(
        self, text: str, prompt: str, voice_name: str, language_code: str, backend_path: Path
    ):
        """Google Cloud TTS (paid, neural-quality)."""
        print("🎙️ Using Google Cloud TTS (paid)...")
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            sample_rate_hertz=24000,
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        backend_path.write_bytes(response.audio_content)
        print(f"🎧 Google Cloud TTS generated → {backend_path.name}")

    async def _generate_gemini_tts(self, text: str, prompt: str, backend_path: Path):
        """Gemini 2.5 Flash TTS (paid, expressive, requires key)."""
        print("🤖 Using Gemini TTS (experimental)...")
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-tts")

        response = model.generate_content(f"{prompt}\n\n{text}")

        # Safe check for audio output
        audio_bytes = None
        try:
            if hasattr(response, "audio"):
                audio_bytes = getattr(response, "audio", None)
            if not audio_bytes and response.candidates:
                parts = response.candidates[0].content.parts
                if parts and hasattr(parts[0], "inline_data"):
                    audio_bytes = parts[0].inline_data.data
        except Exception as e:
            print(f"⚠️ Gemini response parsing failed: {e}")

        if not audio_bytes:
            raise Exception("Gemini TTS failed: no audio output received.")

        backend_path.write_bytes(audio_bytes)
        print(f"🎶 Gemini TTS generated → {backend_path.name}")


# Singleton instance
tts_generator = TTSGenerator()
