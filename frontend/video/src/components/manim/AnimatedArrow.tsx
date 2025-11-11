import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";

interface Props {
  from: { x: number; y: number };
  to: { x: number; y: number };
  color?: string;
  delay?: number;
}

export const AnimatedArrow: React.FC<Props> = ({
  from,
  to,
  color = "#58C4DC",
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 100 },
  });

  const currentX = interpolate(progress, [0, 1], [from.x, to.x]);
  const currentY = interpolate(progress, [0, 1], [from.y, to.y]);

  const angle = Math.atan2(to.y - from.y, to.x - from.x);
  const arrowHeadSize = 20;

  return (
    <AbsoluteFill>
      <svg width="1080" height="1920">
        {/* Main line */}
        <line
          x1={from.x}
          y1={from.y}
          x2={currentX}
          y2={currentY}
          stroke={color}
          strokeWidth={4}
          strokeLinecap="round"
          filter={`drop-shadow(0 0 8px ${color})`}
        />

        {/* Arrowhead */}
        {progress > 0.8 && (
          <g
            transform={`translate(${currentX}, ${currentY}) rotate(${
              (angle * 180) / Math.PI
            })`}
          >
            <polygon
              points={`0,0 -${arrowHeadSize},-${
                arrowHeadSize / 2
              } -${arrowHeadSize},${arrowHeadSize / 2}`}
              fill={color}
              filter={`drop-shadow(0 0 8px ${color})`}
            />
          </g>
        )}
      </svg>
    </AbsoluteFill>
  );
};
