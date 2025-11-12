// frontend/video/src/types/index.ts

export interface SVGElement {
  type:
    | "path"
    | "circle"
    | "rect"
    | "line"
    | "text"
    | "equation"
    | "lucide_icon";
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

// 1. ADD THIS NEW INTERFACE
// This defines the structure for a single subtitle segment
export interface Segment {
  text: string;
  start: number; // in seconds
  end: number; // in seconds
}

export interface Scene {
  title: string;
  narration: string;
  visual: string;
  audio_path: string | null;
  duration_in_seconds: number;
  sound_effect: string;
  visuals: SceneVisuals; // AI-generated SVG scene
  transcription?: Segment[]; // <-- 2. ADD THIS LINE (make it optional)
}

export interface VideoScript {
  script_id: string;
  scenes: Scene[];
  total_duration_seconds: number;
}
