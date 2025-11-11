import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { interpolatePath } from "@remotion/paths";
import { makeCircle, makeRect } from "@remotion/shapes";

interface Props {
  x: number;
  y: number;
  size: number;
  color: string;
}

export const MorphingShape: React.FC<Props> = ({ x, y, size, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const { path: circlePath } = makeCircle({ radius: size / 2 });
  const { path: rectPath } = makeRect({ width: size, height: size });

  const progress = spring({
    frame,
    fps,
    config: { damping: 100 },
  });

  // FIX: Correct interpolatePath usage
  const morphedPath = interpolatePath(progress, circlePath, rectPath);

  const rotation = spring({
    frame,
    fps,
    from: 0,
    to: 360,
    config: { damping: 200, mass: 2 },
  });

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="1080" height="1920">
        <g transform={`translate(${x}, ${y}) rotate(${rotation})`}>
          <path
            d={morphedPath}
            fill="none"
            stroke={color}
            strokeWidth={4}
            filter={`drop-shadow(0 0 15px ${color})`}
          />
        </g>
      </svg>
    </AbsoluteFill>
  );
};
