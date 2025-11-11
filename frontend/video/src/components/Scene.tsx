// frontend/video/src/components/Scene.tsx

import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { ManimBackground } from "./manim/ManimBackground";
import { AIGeneratedScene } from "./manim/AIGeneratedScene";
import { ContentLayer } from "./manim/ContentLayer";
import { ParticleSystem } from "./manim/ParticleSystem";
import type { Scene as SceneType } from "../types";

interface SceneProps {
  scene: SceneType;
  sceneIndex: number;
}

export const Scene: React.FC<SceneProps> = ({ scene, sceneIndex }) => {
  return (
    <AbsoluteFill>
      {/* CONSTANT MANIM BACKGROUND */}
      {/* This now includes the static grid and decorative shapes */}
      <ManimBackground />

      {/* AI-GENERATED SVG ELEMENTS FROM GEMINI */}
      {/* This is the main visual content for the scene */}
      <AIGeneratedScene visuals={scene.visuals} />

      {/* PARTICLES (if AI requests them) */}
      {/* This adds an extra layer of particles on top */}
      {scene.visuals.particles && <ParticleSystem count={40} color="#58C4DC" />}

      {/* CONTENT LAYER - TEXT OVERLAY */}
      {/* This now renders cleanly at the bottom of the screen */}
      <ContentLayer title={scene.title} narration={scene.narration} />

      {/* AUDIO */}
      {scene.audio_path && <Audio src={staticFile(scene.audio_path)} />}

      {scene.sound_effect && (
        <Audio
          src={staticFile(`sounds/${scene.sound_effect}.mp3`)}
          volume={0.3}
        />
      )}
    </AbsoluteFill>
  );
};
