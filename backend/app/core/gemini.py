from typing import Dict
from fastapi import HTTPException
import json
from pathlib import Path
import google.generativeai as genai
from ..config import get_settings

settings = get_settings()

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


class GeminiAnalyzer:
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")

        print("Initializing GeminiAnalyzer...")
        self.model = genai.GenerativeModel(settings.gemini_model)
        print(f"Using Gemini Model: {settings.gemini_model}")

        # Load the prompt template (.md file)
        prompt_path = Path(__file__).parent.parent / "prompts" / "video_script_generation.md"
        if not prompt_path.exists():
            print(f"FATAL ERROR: Prompt template file not found at {prompt_path}")
            raise FileNotFoundError(f"Prompt template file not found: {prompt_path}")

        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()
            print(f"Loaded prompt template from {prompt_path.name} ({len(self.prompt_template)} chars)")

    def _build_prompt(self, paper_text: str, duration_seconds: int) -> str:
        """
        Builds the final Gemini prompt string from the .md template.
        """
        print(f"Building prompt for {duration_seconds}s video...")

        # Substitute duration
        prompt = self.prompt_template.replace("{duration_seconds}", str(duration_seconds))

        allowed_sound_effects = {
            "soft_swoosh",
            "quick_whoosh",
            "slide_in",
            "pop_in",
            "gentle_transition",
            "digital_pulse",
            "cyber_click",
            "circuit_buzz",
            "data_stream",
            "success_chime",
            "completion_bell",
            "achievement_ding",
            "notification_subtle",
            "spark_zap",
            "bubble_pop",
        }

        # Append paper content + instructions
        prompt += f"\n\n---\n\n## PAPER CONTENT\n\n{paper_text}\n\n"
        prompt += "---\n\n"
        prompt += "CREATE THE VIDEO SCRIPT NOW!\n\n"
        prompt += "Return ONLY valid JSON. NO markdown, NO explanations, JUST the JSON.\n"
        prompt += f"{allowed_sound_effects}"

        print("Prompt building complete.")
        return prompt

    async def analyze_paper(self, paper_text: str, duration_seconds: int = 60) -> Dict:
        print(f"\n--- New Analysis Request Received ---")
        print(f"Duration: {duration_seconds}s, Paper Text Length: {len(paper_text)} chars")

        if len(paper_text) > 500000:
            paper_text = paper_text[:500000]
            print("Warning: Paper truncated to 500k chars")

        prompt = self._build_prompt(paper_text, duration_seconds)
        print(f"Final prompt length: {len(prompt)} chars")

        try:
            print("Sending prompt to Gemini API... (This may take a while)")
            response = self.model.generate_content(prompt)
            print("Gemini response received.")

            # Token usage logging
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                print(f"Gemini Token Usage: {response.usage_metadata}")
            else:
                print("Gemini Token Usage: Not available in response.")

            json_str = response.text.strip()
            print(f"Raw response text (first 500 chars): {json_str[:500]}...")

            # Robustly extract JSON object
            print("Robustly finding JSON in response text...")
            start_index = json_str.find("{")
            end_index = json_str.rfind("}")

            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_str = json_str[start_index:end_index + 1]
                print(f"Found JSON object boundaries from index {start_index} to {end_index}.")
            else:
                print("FATAL ERROR: No valid JSON object '{...}' found in response.")
                raise ValueError("No valid JSON object found in response.")

            print("Parsing JSON string...")
            data = json.loads(json_str)
            print("JSON parsing successful.")

            if "scenes" not in data or not isinstance(data["scenes"], list):
                print("FATAL ERROR: Invalid response, 'scenes' array is missing or not a list.")
                raise ValueError("Invalid response: missing 'scenes' array")

            scene_count = len(data["scenes"])
            print(f"Found {scene_count} scenes. Validating each one...")

            if scene_count < 8:
                print(f"Warning: Only {scene_count} scenes generated, expected 8+")

            # ✅ Fixed sound effect validation (robust normalization)
            valid_effects = {
                "soft_swoosh",
                "quick_whoosh",
                "slide_in",
                "pop_in",
                "gentle_transition",
                "digital_pulse",
                "cyber_click",
                "circuit_buzz",
                "data_stream",
                "success_chime",
                "completion_bell",
                "achievement_ding",
                "notification_subtle",
                "spark_zap",
                "bubble_pop",
            }

            for i, scene in enumerate(data["scenes"]):
                print(f"  Validating scene {i+1}/{scene_count} (Title: {scene.get('title', 'N/A')})...")

                required_fields = ["title", "narration", "visual", "visuals"]
                for field in required_fields:
                    if field not in scene:
                        print(f"    ERROR: Scene {i} missing required field: {field}")
                        raise ValueError(f"Scene {i} missing required field: {field}")

                if "svg_elements" not in scene["visuals"]:
                    print(f"    ERROR: Scene {i} missing 'visuals.svg_elements'")
                    raise ValueError(f"Scene {i} missing svg_elements")

                svg_count = len(scene["visuals"]["svg_elements"])
                if svg_count < 1:
                    print(f"    Warning: Scene {i} has 0 svg_elements")

                # --- Fixed normalization here ---
                se = (scene.get("sound_effect") or "").strip().lower().replace("-", "_")

                if se not in valid_effects:
                    print(f" ⚠️ Scene {i} has invalid or missing sound_effect '{scene.get('sound_effect')}', defaulting to 'soft_swoosh'")
                    se = "soft_swoosh"

                scene["sound_effect"] = se
                # --------------------------------

                # Ensure visuals contain defaults
                if "background_color" not in scene["visuals"]:
                    scene["visuals"]["background_color"] = "#0a0e27"
                if "grid" not in scene["visuals"]:
                    scene["visuals"]["grid"] = False
                if "particles" not in scene["visuals"]:
                    scene["visuals"]["particles"] = False

                print(f"  Scene {i+1} OK ({svg_count} SVG elements, sound: {se}).")

            print("✅ All scenes validated successfully.")

            # Summary
            print(f"Generated {len(data['scenes'])} scenes with custom SVG visuals")
            print(f"Total duration: {data.get('total_duration_seconds', 'unknown')}s")

            total_elements = sum(len(scene["visuals"]["svg_elements"]) for scene in data["scenes"])
            print(f"Total SVG elements: {total_elements}")
            if data["scenes"]:
                print(f"Avg elements per scene: {total_elements / len(data['scenes']):.1f}")

            # ✅ Log final sound effect usage summary
            from collections import Counter
            print("Sound effect distribution:", Counter(scene["sound_effect"] for scene in data["scenes"]))

            print("Analysis complete. Returning data.")
            print("--- Analysis Request Finished ---")

            return data

        except json.JSONDecodeError as e:
            print(f"FATAL ERROR: JSON parse error: {e}")
            print(f"Raw response (first 1000 chars):\n{json_str[:1000]}")
            raise HTTPException(status_code=500, detail=f"Invalid JSON from Gemini: {str(e)}")

        except Exception as e:
            print(f"FATAL ERROR: An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


gemini_analyzer = GeminiAnalyzer()
