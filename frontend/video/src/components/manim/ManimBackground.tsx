import React from "react";
import { AbsoluteFill } from "remotion";
import { AnimatedGrid } from "./AnimatedGrid";
import { loadFont } from "@remotion/google-fonts/JetBrainsMono";

// ONE FONT FOR ENTIRE VIDEO
export const { fontFamily: MANIM_FONT } = loadFont();

export const ManimBackground: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0e27" }}>
      {/* Animated grid - always present */}
      <AnimatedGrid />

      {/* All the old <AnimatedCircle />, <MorphingShape />, 
        and <AnimatedArrow /> components have been DELETED.
        
        Your <AIGeneratedScene /> component is now 
        fully responsible for all visual elements.
      */}
    </AbsoluteFill>
  );
};
