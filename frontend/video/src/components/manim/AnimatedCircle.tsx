import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { makeCircle } from "@remotion/shapes";

interface Props {
  x: number;
  y: number;
  radius: number;
  color: string;
  delay?: number;
}

export const AnimatedCircle: React.FC<Props> = ({
  x,
  y,
  radius,
  color,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame: frame - delay,
    fps,
    config: { damping: 80, stiffness: 200 },
  });

  const { path } = makeCircle({ radius });

  return (
    <AbsoluteFill>
      <svg width="1080" height="1920">
        <g transform={`translate(${x}, ${y}) scale(${scale})`}>
          <path
            d={path}
            fill="none"
            stroke={color}
            strokeWidth={4}
            filter={`drop-shadow(0 0 10px ${color})`}
          />
        </g>
      </svg>
    </AbsoluteFill>
  );
};
