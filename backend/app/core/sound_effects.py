from typing import Dict

# Map visual types to sound effect types for Remotion
SOUND_EFFECT_MAP: Dict[str, str] = {
    "title_card": "whoosh_impact",      # Dramatic entry
    "explainer": "soft_ambient",        # Subtle background
    "key_point": "pop_sequence",        # Pop for each bullet
    "quote": "ethereal_chime",          # Thoughtful tone
    "statistic": "digital_beep",        # Tech/data sound
    "comparison": "transition_swoosh",  # Side-to-side movement
    "timeline": "tick_sequence",        # Clock/progress sounds
    "conclusion": "finale_chord"        # Ending impact
}


def get_sound_effect(visual_type: str) -> str:
    """
    Get the sound effect type for a visual style.
    Returns the sound effect identifier that Remotion will use.
    """
    return SOUND_EFFECT_MAP.get(visual_type, "soft_ambient")
