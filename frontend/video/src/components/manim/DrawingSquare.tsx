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
  size: number;
  color: string;
}

export const DrawingSquare: React.FC<Props> = ({ x, y, size, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame, fps, config: { damping: 100 } });
  const perimeter = size * 4;
  const dashOffset = perimeter * (1 - progress);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="1080" height="1920">
        <rect
          x={x - size / 2}
          y={y - size / 2}
          width={size}
          height={size}
          fill="none"
          stroke={color}
          strokeWidth={4}
          strokeDasharray={perimeter}
          strokeDashoffset={dashOffset}
          filter={`drop-shadow(0 0 15px ${color})`}
        />
      </svg>
    </AbsoluteFill>
  );
};
