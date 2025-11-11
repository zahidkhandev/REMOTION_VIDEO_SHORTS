import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

export const AnimatedGrid: React.FC = () => {
  const frame = useCurrentFrame();

  const gridSize = 60;
  const cols = Math.ceil(1080 / gridSize);
  const rows = Math.ceil(1920 / gridSize);

  return (
    <AbsoluteFill>
      <svg width="1080" height="1920" style={{ position: "absolute" }}>
        {/* Vertical lines */}
        {Array.from({ length: cols + 1 }).map((_, i) => {
          const opacity = interpolate(frame, [i * 2, i * 2 + 20], [0, 0.15], {
            extrapolateRight: "clamp",
          });

          return (
            <line
              key={`v-${i}`}
              x1={i * gridSize}
              y1={0}
              x2={i * gridSize}
              y2={1920}
              stroke="#58C4DC"
              strokeWidth={1}
              opacity={opacity}
            />
          );
        })}

        {/* Horizontal lines */}
        {Array.from({ length: rows + 1 }).map((_, i) => {
          const opacity = interpolate(frame, [i * 2, i * 2 + 20], [0, 0.15], {
            extrapolateRight: "clamp",
          });

          return (
            <line
              key={`h-${i}`}
              x1={0}
              y1={i * gridSize}
              x2={1080}
              y2={i * gridSize}
              stroke="#58C4DC"
              strokeWidth={1}
              opacity={opacity}
            />
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};
