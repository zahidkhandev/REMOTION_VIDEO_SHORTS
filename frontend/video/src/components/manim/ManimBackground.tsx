import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { AnimatedGrid } from "./AnimatedGrid";
import { AnimatedCircle } from "./AnimatedCircle";
import { MorphingShape } from "./MorphingShape";
import { AnimatedArrow } from "./AnimatedArrow";
import { loadFont } from "@remotion/google-fonts/JetBrainsMono";

// ONE FONT FOR ENTIRE VIDEO
export const { fontFamily: MANIM_FONT } = loadFont();

export const ManimBackground: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0e27" }}>
      {/* Animated grid - always present */}
      <AnimatedGrid />

      {/* Decorative shapes - scattered across canvas */}
      <AnimatedCircle x={150} y={250} radius={60} color="#58C4DC" delay={0} />
      <AnimatedCircle x={900} y={400} radius={80} color="#FF6B6B" delay={5} />
      <AnimatedCircle x={200} y={1500} radius={70} color="#4ECDC4" delay={10} />
      <AnimatedCircle x={850} y={1700} radius={90} color="#FFE66D" delay={15} />

      {/* Morphing shapes */}
      <MorphingShape x={100} y={700} size={100} color="#58C4DC" />
      <MorphingShape x={950} y={1000} size={120} color="#FF6B6B" />
      <MorphingShape x={120} y={1300} size={90} color="#4ECDC4" />

      {/* Connecting arrows */}
      <Sequence from={20}>
        <AnimatedArrow
          from={{ x: 150, y: 250 }}
          to={{ x: 540, y: 600 }}
          color="#58C4DC"
          delay={0}
        />
      </Sequence>

      <Sequence from={30}>
        <AnimatedArrow
          from={{ x: 900, y: 400 }}
          to={{ x: 540, y: 800 }}
          color="#FF6B6B"
          delay={0}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
