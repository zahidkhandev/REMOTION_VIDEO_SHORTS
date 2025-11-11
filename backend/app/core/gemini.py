from typing import Dict
from fastapi import HTTPException
import json

# Import Gemini
try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")

from ..config import get_settings

settings = get_settings()

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)  # type: ignore


class GeminiAnalyzer:
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        self.model = genai.GenerativeModel(settings.gemini_model)  # type: ignore
    
    async def analyze_paper(self, paper_text: str, duration_seconds: int = 60) -> Dict:
        """
        Analyze research paper and generate structured video script.
        NotebookLM-inspired visual generation using Gemini 2.5 Flash.
        """
        # Gemini 2.5 Flash has 1M+ token context window - use the full paper!
        # Truncate only if extremely long (>500k chars = ~125k tokens)
        if len(paper_text) > 500000:
            paper_text_truncated = paper_text[:500000]
            print(f"Warning: Paper truncated from {len(paper_text)} to 500k chars")
        else:
            paper_text_truncated = paper_text
            print(f"Processing full paper: {len(paper_text)} characters")
        
        prompt = f"""
You are an expert science communicator creating engaging short-form video scripts in the style of NotebookLM's video overviews.

Analyze the following research paper and create a {duration_seconds}-second video script for a vertical video (YouTube Shorts/TikTok format).

CRITICAL REQUIREMENTS:
1. Generate 6-10 scenes total
2. Each scene should be 5-12 seconds of narration
3. Use varied visual styles to keep engagement high
4. Narration must be conversational, engaging, and hook-driven
5. Use simple language - explain complex ideas simply
6. Include a strong hook in the first scene
7. End with a compelling conclusion
8. Make it cinematic and dramatic like a movie trailer

AVAILABLE VISUAL TYPES (use variety!):
- "title_card": Big, bold opening statement (use for scene 1)
- "explainer": Main explanatory content with text emphasis
- "key_point": List of important insights (bullet format)
- "quote": Highlight important quotes or key statements
- "statistic": Emphasize numbers and data (format: "number: label")
- "comparison": Side-by-side comparison of concepts
- "timeline": Sequential process or steps
- "conclusion": Closing statement with call-to-action

OUTPUT FORMAT (Must be valid JSON):
{{
  "scenes": [
    {{
      "title": "Hook title or main text (max 12 words)",
      "narration": "Engaging 1-2 sentence narration that sounds natural when spoken.",
      "visual": "title_card"
    }}
  ]
}}

VISUAL STYLE GUIDE:
- title_card: "AI Breakthrough: What You Need to Know"
- explainer: Title: "The Core Innovation", Narration: "Researchers developed a new approach..."
- key_point: Title: "Three key findings • 40% improvement • Novel architecture • Real-world impact"
- statistic: Title: "92%: Accuracy Rate", Narration: "The model achieved unprecedented accuracy"
- quote: Title: "This changes everything", Narration: "As the lead researcher stated..."
- comparison: Title: "Before vs After", Narration: "The difference is striking..."
- timeline: Title: "The Three-Step Process", Narration: "First, data collection. Then analysis. Finally, results."

PAPER TEXT (FULL PAPER):
---
{paper_text_truncated}
---

Generate ONLY the JSON, no extra text. No markdown formatting.
"""
        
        try:
            response = self.model.generate_content(prompt)
            json_str = response.text.strip()
            
            # Clean up markdown formatting - THIS IS THE LINE YOU KEEP BREAKING!
            json_str = json_str.replace("```json", "")
            json_str = json_str.replace("```", "")
            json_str = json_str.strip()
            
            # Remove extra whitespace
            lines = [line.strip() for line in json_str.split('\n') if line.strip()]
            json_str = '\n'.join(lines)
            
            data = json.loads(json_str)
            
            if "scenes" not in data or not isinstance(data["scenes"], list):
                raise ValueError("Invalid response structure: missing 'scenes' array")
            
            # Validate scenes
            for i, scene in enumerate(data["scenes"]):
                if "title" not in scene or "narration" not in scene or "visual" not in scene:
                    raise ValueError(f"Scene {i} missing required fields")
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gemini response: {e}")
            print(f"Raw response: {response.text}")
            raise HTTPException(
                status_code=500,
                detail=f"Gemini returned invalid JSON: {str(e)}"
            )
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze paper: {str(e)}"
            )


# Singleton instance
gemini_analyzer = GeminiAnalyzer()
