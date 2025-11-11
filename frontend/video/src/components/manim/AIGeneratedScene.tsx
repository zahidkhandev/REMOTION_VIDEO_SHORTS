import React from "react";
import { AbsoluteFill } from "remotion";
import { DynamicSVGRenderer } from "./DynamicSVGRenderer";
import type { SceneVisuals } from "../../types";

interface Props {
  visuals: SceneVisuals;
}

export const AIGeneratedScene: React.FC<Props> = ({ visuals }) => {
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <svg width="1080" height="1920">
        {visuals.svg_elements.map((element, index) => (
          <DynamicSVGRenderer key={index} element={element} />
        ))}
      </svg>
    </AbsoluteFill>
  );
};
