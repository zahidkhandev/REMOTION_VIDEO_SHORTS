import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface Props {
  x: number;
  y: number;
  func: (x: number, y: number) => number;
  color?: string;
}

export const Graph3D: React.FC<Props> = ({ x, y, func, color = "#58C4DC" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame, fps, config: { damping: 100 } });
  const rotation = progress * 360;

  const gridSize = 10;
  const scale = 20;

  const points: Array<{ x: number; y: number; z: number }> = [];

  for (let i = -5; i <= 5; i++) {
    for (let j = -5; j <= 5; j++) {
      if (Math.random() < progress) {
        const z = func(i / 2, j / 2);
        points.push({ x: i * scale, y: j * scale, z: z * scale });
      }
    }
  }

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="1080" height="1920">
        <g transform={`translate(${x}, ${y}) rotateY(${rotation})`}>
          {points.map((p, i) => {
            const screenX = p.x + p.z * 0.5;
            const screenY = p.y - p.z * 0.3;

            return (
              <circle
                key={i}
                cx={screenX}
                cy={screenY}
                r={3}
                fill={color}
                opacity={0.8}
                filter={`drop-shadow(0 0 5px ${color})`}
              />
            );
          })}
        </g>
      </svg>
    </AbsoluteFill>
  );
};
