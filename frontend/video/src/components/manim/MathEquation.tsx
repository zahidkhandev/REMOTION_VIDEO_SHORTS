import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";

interface Props {
  equation: string;
  color?: string;
}

export const MathEquation: React.FC<Props> = ({
  equation,
  color = "#58C4DC",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    config: { damping: 100, mass: 0.5 },
  });

  const chars = equation.split("");

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background: "radial-gradient(circle, #0a0e27 0%, #000000 100%)",
      }}
    >
      <div style={{ display: "flex", transform: `scale(${scale})` }}>
        {chars.map((char, i) => {
          const charSpring = spring({
            frame: frame - i * 2,
            fps,
            config: { damping: 80 },
          });

          const y = interpolate(charSpring, [0, 1], [50, 0]);

          return (
            <span
              key={i}
              style={{
                fontSize: 120,
                fontFamily: "monospace",
                fontWeight: 700,
                color,
                opacity: charSpring,
                transform: `translateY(${y}px)`,
                marginRight: char === " " ? 30 : 5,
                textShadow: `0 0 20px ${color}`,
              }}
            >
              {char}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
