from typing import Dict
from fastapi import HTTPException
import json
import yaml
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
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        prompt_path = Path(__file__).parent.parent / "prompts" / "video_script_notebooklm.yaml"
        
        if not prompt_path.exists():
            print("Warning: NotebookLM YAML not found, trying default...")
            prompt_path = Path(__file__).parent.parent / "prompts" / "video_script_generation.yaml"
        
        # This still requires you to fix the indentation error in the YAML file itself.
        # The parser will fail here if the YAML is invalid.
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            print(f"Loaded prompt config from {prompt_path.name}")
    
    def _build_prompt_from_yaml(self, paper_text: str, duration_seconds: int) -> str:
        cfg = self.config
        
        prompt = f"""{cfg['system_role']}

{cfg['mission'].format(duration_seconds=duration_seconds)}

---

## TIMING REQUIREMENTS

"""
        for key, value in cfg['timing_requirements'].items():
            if isinstance(value, dict):
                prompt += f"**{key.replace('_', ' ').title()}:**\n"
                for k, v in value.items():
                    prompt += f"  - {k}: {v}\n"
            else:
                prompt += f"- {key}: {value.format(duration_seconds=duration_seconds)}\n"
        
        prompt += "\n---\n\n## NARRATION GUIDELINES\n\n"
        
        # FIX 1: Changed 'style' to 'overall_approach'
        prompt += f"{cfg['narration_guidelines']['overall_approach']}\n\n"
        prompt += f"**Word count:** {cfg['narration_guidelines']['word_count']}\n"
        
        # FIX 2: Changed 'tone' to 'tone_examples' and formatted it
        prompt += f"**Tone:**\n"
        if 'tone_examples' in cfg['narration_guidelines'] and 'good_tone' in cfg['narration_guidelines']['tone_examples']:
            for tone in cfg['narration_guidelines']['tone_examples']['good_tone']:
                prompt += f"- {tone}\n"
        prompt += "\n"
        
        prompt += "**AVOID:**\n"
        # FIX 3: Changed 'avoid_phrases' to 'forbidden_phrases' and looped through sub-keys
        if 'forbidden_phrases' in cfg['narration_guidelines']:
            for phrase_type, phrases in cfg['narration_guidelines']['forbidden_phrases'].items():
                if isinstance(phrases, list):
                    for phrase in phrases:
                        prompt += f"- {phrase}\n"
        
        prompt += "\n**PREFER:**\n"
        # FIX 4: Changed 'prefer_phrases' to 'preferred_phrases' and looped through sub-keys
        if 'preferred_phrases' in cfg['narration_guidelines']:
            for phrase_type, phrases in cfg['narration_guidelines']['preferred_phrases'].items():
                if isinstance(phrases, list):
                    for phrase in phrases:
                        prompt += f"- {phrase}\n"
        
        prompt += "\n---\n\n## VISUAL PATTERNS\n\n"
        prompt += "Use a DIFFERENT pattern for EACH scene:\n\n"
        
        for pattern_key, pattern in cfg['visual_patterns'].items():
            prompt += f"**{pattern['name']}:** {pattern['description']}\n"
            if 'best_for' in pattern and isinstance(pattern['best_for'], list):
                prompt += f"  Best for: {', '.join(pattern['best_for'])}\n\n"
        
        prompt += "\n---\n\n## SVG ELEMENT TYPES\n\n"
        
        for elem_type, elem_info in cfg['svg_element_library'].items():
            prompt += f"### {elem_type.upper()}\n"
            if 'description' in elem_info:
                prompt += f"{elem_info['description']}\n"
            
            # FIX 5 (A): Check for 'data_format' and 'type' inside it
            if 'data_format' in elem_info and 'type' in elem_info['data_format']:
                prompt += f"**Data format:** {elem_info['data_format']['type']}\n"

            # FIX 5 (B): Check for 'data_format' and 'examples' inside it, then join .values()
            if 'data_format' in elem_info and 'examples' in elem_info['data_format']:
                # Check if 'examples' is a dictionary before calling .values()
                if isinstance(elem_info['data_format']['examples'], dict):
                    example_str = ", ".join(elem_info['data_format']['examples'].values())
                    prompt += f"**Examples:** {example_str}\n"
            
            if 'code_example' in elem_info:
                 prompt += f"**Example:**\n```json\n{elem_info['code_example'].strip()}\n```\n\n"

        
        prompt += "\n---\n\n## COLOR PALETTE\n\n"
        
        for color_key, color_info in cfg['color_palette'].items():
            if isinstance(color_info, dict) and 'hex' in color_info:
                prompt += f"**{color_info['name']}** (`{color_info['hex']}`)\n"
                if 'usage' in color_info:
                    prompt += f"  Usage: {color_info['usage']}\n\n"
        
        prompt += "\n---\n\n## REQUIRED OUTPUT\n\n"
        prompt += "Return ONLY valid JSON following this schema:\n\n"
        
        # FIX 6: Dump the json_schema from config, not an empty string
        if 'json_schema' in cfg:
            prompt += f"```json\n{json.dumps(cfg['json_schema'], indent=2)}\n```\n\n"
        else:
            prompt += "```json\n{...}\n```\n\n"

        
        prompt += "\n---\n\n## STRICT REQUIREMENTS\n\n"
        
        if 'strict_requirements' in cfg:
            for req in cfg['strict_requirements']:
                prompt += f"- {req.format(duration_seconds=duration_seconds)}\n"
        
        prompt += f"\n---\n\n## PAPER CONTENT\n\n{paper_text}\n\n"
        prompt += "---\n\n"
        prompt += "CREATE THE VIDEO SCRIPT NOW!\n\n"
        prompt += "Return ONLY valid JSON. NO markdown, NO explanations, JUST the JSON.\n"
        
        return prompt
    
    async def analyze_paper(self, paper_text: str, duration_seconds: int = 60) -> Dict:
        if len(paper_text) > 500000:
            paper_text = paper_text[:500000]
            print("Warning: Paper truncated to 500k chars")
        
        prompt = self._build_prompt_from_yaml(paper_text, duration_seconds)
        
        print(f"Generated prompt: {len(prompt)} chars")
        
        try:
            response = self.model.generate_content(prompt)
            json_str = response.text.strip()
            
            # --- START FIX ---
            # Robustly find the JSON object within the response text,
            # ignoring markdown fences or other explanatory text.
            start_index = json_str.find('{')
            end_index = json_str.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_str = json_str[start_index : end_index + 1]
            else:
                # If no {} found, parsing will fail, raise an error
                raise ValueError("No valid JSON object found in response.")
            # --- END FIX ---
            
            data = json.loads(json_str)
            
            if "scenes" not in data or not isinstance(data["scenes"], list):
                raise ValueError("Invalid response: missing 'scenes' array")
            
            if len(data["scenes"]) < 8:
                print(f"Warning: Only {len(data['scenes'])} scenes generated, expected 8+")
            
            for i, scene in enumerate(data["scenes"]):
                required = ["title", "narration", "visual", "visuals"]
                for field in required:
                    if field not in scene:
                        raise ValueError(f"Scene {i} missing required field: {field}")
                
                if "svg_elements" not in scene["visuals"]:
                    raise ValueError(f"Scene {i} missing svg_elements")
                
                # This warning is subjective, can be adjusted
                if len(scene["visuals"]["svg_elements"]) < 1:
                    print(f"Warning: Scene {i} has 0 svg_elements")
                
                if "sound_effect" not in scene:
                    scene["sound_effect"] = "soft_ambient"
                
                if "background_color" not in scene["visuals"]:
                    scene["visuals"]["background_color"] = self.config['color_palette']['background']['hex']
                
                if "grid" not in scene["visuals"]:
                    scene["visuals"]["grid"] = False
                if "particles" not in scene["visuals"]:
                    scene["visuals"]["particles"] = False
            
            print(f"Generated {len(data['scenes'])} scenes with custom SVG visuals")
            print(f"Total duration: {data.get('total_duration_seconds', 'unknown')}s")
            
            total_elements = sum(len(scene["visuals"]["svg_elements"]) for scene in data["scenes"])
            print(f"Total SVG elements: {total_elements}")
            if data["scenes"]:
                print(f"Avg elements per scene: {total_elements / len(data['scenes']):.1f}")
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response (first 1000 chars):\n{response.text[:1000]}")
            raise HTTPException(status_code=500, detail=f"Invalid JSON from Gemini: {str(e)}")
        except Exception as e:
            print(f"Gemini error: {e}")
            # Propagate the original error message for better debugging
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


gemini_analyzer = GeminiAnalyzer()