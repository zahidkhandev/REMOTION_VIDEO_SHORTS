// frontend/video/src/types/index.ts

export interface SVGElement {
  type: "path" | "circle" | "rect" | "line" | "text" | "equation";
  data: string;
  x: number;
  y: number;
  color: string;
  stroke_width: number;
  animation: "draw" | "fade" | "scale" | "morph" | "pulse";
  delay: number;
}

export interface SceneVisuals {
  svg_elements: SVGElement[];
  background_color: string;
  particles: boolean;
  grid: boolean;
}

export interface Scene {
  title: string;
  narration: string;
  visual:
    | "title_card"
    | "explainer"
    | "key_point"
    | "quote"
    | "statistic"
    | "comparison"
    | "timeline"
    | "conclusion";
  audio_path: string | null;
  duration_in_seconds: number;
  sound_effect: string;
  visuals: SceneVisuals; // AI-generated SVG scene
}

export interface VideoScript {
  script_id: string;
  scenes: Scene[];
  total_duration_seconds: number;
}
