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
  radius: number;
  color: string;
  strokeWidth?: number;
}

export const DrawingCircle: React.FC<Props> = ({
  x,
  y,
  radius,
  color,
  strokeWidth = 4,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame, fps, config: { damping: 100 } });
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - progress);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="1080" height="1920">
        <circle
          cx={x}
          cy={y}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          filter={`drop-shadow(0 0 15px ${color})`}
        />
      </svg>
    </AbsoluteFill>
  );
};
