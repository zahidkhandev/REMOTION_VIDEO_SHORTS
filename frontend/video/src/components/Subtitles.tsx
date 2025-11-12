import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig, // 1. Import useVideoConfig
} from "remotion";
import { MANIM_FONT } from "./manim";

// 2. Define the new data structure (based on Whisper's output)
// This data would be loaded from the JSON files mentioned in the docs
export interface Segment {
  text: string;
  start: number; // in seconds
  end: number; // in seconds
}

interface SubtitleProps {
  // 3. Update props to accept an array of segments
  segments: Segment[];
}

/**
 * Styles for the subtitle container.
 * Sits in the bottom "safe area" (y > 1700).
 */
const subtitleContainerStyle: React.CSSProperties = {
  justifyContent: "flex-end",
  alignItems: "center",
  paddingBottom: 200, // Positions text ~1720px, well within safe area
  pointerEvents: "none", // Allow clicks to pass through
};

/**
 * Styles for the subtitle text itself.
 */
const subtitleTextStyle: React.CSSProperties = {
  fontFamily: MANIM_FONT,
  fontSize: 30,
  color: "white",
  textAlign: "center",
  width: "90%", // Max width, 90% of 1080px = 972px
  maxWidth: 972,
  textShadow: "0 4px 10px rgba(0,0,0,0.8)", // Strong shadow for readability
  lineHeight: 1.4,
  fontWeight: 500,

  // 4. Add CSS to enforce a 2-line limit
  overflow: "hidden",
  display: "-webkit-box",
  WebkitLineClamp: 2, // Explicitly limit to 2 lines
  WebkitBoxOrient: "vertical",
};

export const Subtitles: React.FC<SubtitleProps> = ({ segments }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig(); // 5. Get FPS
  const currentTimeInSeconds = frame / fps; // 6. Calculate current time

  // 7. Find the currently active segment
  // Find the segment where the current time is between its start and end
  const activeSegment = segments.find((segment) => {
    return (
      currentTimeInSeconds >= segment.start &&
      currentTimeInSeconds <= segment.end
    );
  });

  // 8. If no segment is active, render nothing
  if (!activeSegment) {
    return null;
  }

  // 9. Render the active segment's text
  return (
    <AbsoluteFill style={subtitleContainerStyle}>
      <div style={subtitleTextStyle}>{activeSegment.text}</div>
    </AbsoluteFill>
  );
};
