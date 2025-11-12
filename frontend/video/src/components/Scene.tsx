// frontend/video/src/components/Scene.tsx

import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { ManimBackground } from "./manim/ManimBackground";
import { AIGeneratedScene } from "./manim/AIGeneratedScene";
import { ParticleSystem } from "./manim/ParticleSystem";

// Import the new, timestamp-aware Subtitles component
import { Subtitles } from "./Subtitles";

// Import your main scene data type
// (This will now correctly include 'transcription?: Segment[]')
import type { Scene as SceneType } from "../types";

interface SceneProps {
  scene: SceneType;
  sceneIndex: number;
}

export const Scene: React.FC<SceneProps> = ({ scene, sceneIndex }) => {
  // We no longer need useVideoConfig for the subtitles
  // as the Subtitles component handles its own timing.

  return (
    <AbsoluteFill>
      {/* CONSTANT MANIM BACKGROUND */}
      <ManimBackground />

      {/* AI-GENERATED SVG ELEMENTS FROM GEMINI */}
      <AIGeneratedScene visuals={scene.visuals} />

      {/* PARTICLE EFFECTS (if enabled by Gemini visuals) */}
      {scene.visuals.particles && <ParticleSystem count={40} color="#58C4DC" />}

      {/* AUDIO - MAIN NARRATION */}
      {scene.audio_path && (
        <Audio src={staticFile(scene.audio_path)} playbackRate={1} volume={1} />
      )}

      {/* AUDIO - SOUND EFFECT */}
      {scene.sound_effect && (
        <Audio
          src={staticFile(`sounds/${scene.sound_effect}.wav`)}
          volume={0.3}
        />
      )}

      {/*
       * RENDER THE SUBTITLES
       * This code is correct. It checks if 'transcription' exists
       * before passing it to the Subtitles component.
       */}
      {scene.transcription && <Subtitles segments={scene.transcription} />}
    </AbsoluteFill>
  );
};
