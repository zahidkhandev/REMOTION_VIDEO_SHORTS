import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";

interface Props {
  func: (x: number) => number;
  color?: string;
  xRange?: [number, number];
  yRange?: [number, number];
}

export const Graph: React.FC<Props> = ({
  func,
  color = "#58C4DC",
  xRange = [-5, 5],
  yRange = [-5, 5],
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame, fps, config: { damping: 100 } });

  const width = 1080;
  const height = 1920;
  const centerX = width / 2;
  const centerY = height / 2;

  const scaleX = width / (xRange[1] - xRange[0]);
  const scaleY = height / (yRange[1] - yRange[0]);

  const points = Array.from({ length: 200 }, (_, i) => {
    const t = i / 199;
    const x = xRange[0] + t * (xRange[1] - xRange[0]);
    const y = func(x);

    const screenX = centerX + x * scaleX * 0.3;
    const screenY = centerY - y * scaleY * 0.3;

    return { x: screenX, y: screenY };
  });

  const visiblePoints = Math.floor(points.length * progress);

  const pathData = points
    .slice(0, visiblePoints)
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ");

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <svg width={width} height={height}>
        {/* Axes */}
        <line
          x1={0}
          y1={centerY}
          x2={width}
          y2={centerY}
          stroke="#333"
          strokeWidth={2}
        />
        <line
          x1={centerX}
          y1={0}
          x2={centerX}
          y2={height}
          stroke="#333"
          strokeWidth={2}
        />

        {/* Function curve */}
        <path
          d={pathData}
          fill="none"
          stroke={color}
          strokeWidth={5}
          strokeLinecap="round"
          filter={`drop-shadow(0 0 10px ${color})`}
        />
      </svg>
    </AbsoluteFill>
  );
};
