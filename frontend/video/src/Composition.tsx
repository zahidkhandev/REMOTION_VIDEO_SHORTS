import React from "react";
import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { Scene } from "./components/Scene";
import type { VideoScript } from "./types";

// Remove React.FC<VideoScript>, use regular function
export const PaperVideoComposition = (props: VideoScript) => {
  const { fps } = useVideoConfig();
  let frameStart = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {props.scenes.map((scene, index) => {
        const durationInFrames = Math.ceil(scene.duration_in_seconds * fps);

        const component = (
          <Sequence
            key={index}
            from={frameStart}
            durationInFrames={durationInFrames}
            name={`Scene ${index + 1}: ${scene.title}`}
          >
            <Scene scene={scene} sceneIndex={index} />
          </Sequence>
        );

        frameStart += durationInFrames;
        return component;
      })}
    </AbsoluteFill>
  );
};
