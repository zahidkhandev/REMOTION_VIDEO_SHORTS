import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";

interface Props {
  x: number;
  y: number;
  scale?: number;
}

export const DrawingRocket: React.FC<Props> = ({ x, y, scale = 1 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const drawProgress = spring({ frame, fps, config: { damping: 100 } });
  const rocketY = interpolate(drawProgress, [0, 1], [0, -100]);

  // Rocket paths (simplified SVG)
  const rocketPath = "M50,0 L60,40 L70,80 L50,100 L30,80 L40,40 Z";
  const flameLeftPath = "M40,100 Q35,120 30,140";
  const flameRightPath = "M60,100 Q65,120 70,140";

  const totalLength = 400;
  const dashOffset = totalLength * (1 - drawProgress);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="1080" height="1920">
        <g transform={`translate(${x}, ${y + rocketY}) scale(${scale})`}>
          {/* Rocket body */}
          <path
            d={rocketPath}
            fill="none"
            stroke="#58C4DC"
            strokeWidth={3}
            strokeDasharray={totalLength}
            strokeDashoffset={dashOffset}
            filter="drop-shadow(0 0 10px #58C4DC)"
          />

          {/* Flames */}
          {drawProgress > 0.7 && (
            <>
              <path
                d={flameLeftPath}
                fill="none"
                stroke="#FF6B6B"
                strokeWidth={3}
                opacity={drawProgress}
                filter="drop-shadow(0 0 10px #FF6B6B)"
              />
              <path
                d={flameRightPath}
                fill="none"
                stroke="#FFE66D"
                strokeWidth={3}
                opacity={drawProgress}
                filter="drop-shadow(0 0 10px #FFE66D)"
              />
            </>
          )}

          {/* Window */}
          {drawProgress > 0.5 && (
            <circle
              cx="50"
              cy="30"
              r="8"
              fill="#58C4DC"
              opacity={drawProgress}
            />
          )}
        </g>
      </svg>
    </AbsoluteFill>
  );
};
