// frontend/video/src/components/manim/ContentLayer.tsx

import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import { MANIM_FONT } from "./ManimBackground";

interface Props {
  title: string;
  narration: string;
}

export const ContentLayer: React.FC<Props> = ({ title, narration }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring for the entire block
  const blockSpring = spring({
    frame,
    fps,
    config: { damping: 100, stiffness: 100 },
  });

  // Animate the block fading in and sliding up from the bottom
  const blockY = interpolate(blockSpring, [0, 1], [100, 0]);
  const blockOpacity = interpolate(blockSpring, [0, 0.5], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        // Align content to the BOTTOM of the screen
        justifyContent: "flex-end",
        padding: "0 60px 80px 60px", // Padding on sides and bottom
        pointerEvents: "none",
        opacity: blockOpacity,
        transform: `translateY(${blockY}px)`,
      }}
    >
      {/* This div is now just a container, no background or border */}
      <div
        style={{
          maxWidth: 900,
          margin: "0 auto", // Center the container
        }}
      >
        <h1
          style={{
            fontSize: 56, // Slightly smaller
            fontWeight: 700,
            color: "#58C4DC",
            fontFamily: MANIM_FONT,
            marginBottom: 20, // Tighter spacing
            textAlign: "center",
            textShadow: "0 0 20px rgba(88, 196, 220, 0.6)",
          }}
        >
          {title}
        </h1>
        <p
          style={{
            fontSize: 32, // Slightly smaller
            color: "#E0E0E0",
            fontFamily: MANIM_FONT,
            lineHeight: 1.6, // Tighter line height
            textAlign: "center",
          }}
        >
          {narration}
        </p>
      </div>
    </AbsoluteFill>
  );
};
