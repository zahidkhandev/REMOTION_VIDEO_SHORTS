import React from "react";
import {
  AbsoluteFill,
  random,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface Props {
  count?: number;
  color?: string;
}

export const ParticleSystem: React.FC<Props> = ({
  count = 50,
  color = "#58C4DC",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const particles = Array.from({ length: count }, (_, i) => {
    const seed = i * 1000;
    const angle = random(`angle-${seed}`) * Math.PI * 2;
    const speed = random(`speed-${seed}`) * 5 + 2;

    const progress = spring({
      frame: frame - i * 2,
      fps,
      config: { damping: 100 },
    });

    const distance = progress * speed * 100;

    return {
      x: 540 + Math.cos(angle) * distance,
      y: 960 + Math.sin(angle) * distance,
      opacity: 1 - progress,
      size: random(`size-${seed}`) * 5 + 2,
    };
  });

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="1080" height="1920">
        {particles.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r={p.size}
            fill={color}
            opacity={p.opacity}
            filter={`blur(${(1 - p.opacity) * 2}px)`}
          />
        ))}
      </svg>
    </AbsoluteFill>
  );
};
