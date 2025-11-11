import React from "react";
import { spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import type { SVGElement } from "../../types";
import { MANIM_FONT } from "./ManimBackground";

interface Props {
  element: SVGElement;
}

export const DynamicSVGRenderer: React.FC<Props> = ({ element }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - element.delay,
    fps,
    config: { damping: 100 },
  });

  // CIRCLE
  if (element.type === "circle") {
    const radius = parseFloat(element.data);

    if (element.animation === "draw") {
      const circumference = 2 * Math.PI * radius;
      const dashOffset = circumference * (1 - progress);

      return (
        <circle
          cx={element.x}
          cy={element.y}
          r={radius}
          fill="none"
          stroke={element.color}
          strokeWidth={element.stroke_width}
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          filter={`drop-shadow(0 0 10px ${element.color})`}
        />
      );
    }

    if (element.animation === "scale") {
      return (
        <circle
          cx={element.x}
          cy={element.y}
          r={radius * progress}
          fill="none"
          stroke={element.color}
          strokeWidth={element.stroke_width}
          opacity={progress}
          filter={`drop-shadow(0 0 10px ${element.color})`}
        />
      );
    }

    if (element.animation === "pulse") {
      const pulse = 1 + Math.sin((frame - element.delay) * 0.2) * 0.1;
      return (
        <circle
          cx={element.x}
          cy={element.y}
          r={radius * pulse}
          fill="none"
          stroke={element.color}
          strokeWidth={element.stroke_width}
          opacity={progress}
          filter={`drop-shadow(0 0 ${10 * pulse}px ${element.color})`}
        />
      );
    }

    return (
      <circle
        cx={element.x}
        cy={element.y}
        r={radius}
        fill="none"
        stroke={element.color}
        strokeWidth={element.stroke_width}
        opacity={progress}
        filter={`drop-shadow(0 0 10px ${element.color})`}
      />
    );
  }

  // RECTANGLE
  if (element.type === "rect") {
    const [width, height] = element.data.split(",").map(parseFloat);
    const perimeter = (width + height) * 2;

    if (element.animation === "draw") {
      const dashOffset = perimeter * (1 - progress);

      return (
        <rect
          x={element.x - width / 2}
          y={element.y - height / 2}
          width={width}
          height={height}
          fill="none"
          stroke={element.color}
          strokeWidth={element.stroke_width}
          strokeDasharray={perimeter}
          strokeDashoffset={dashOffset}
          filter={`drop-shadow(0 0 10px ${element.color})`}
        />
      );
    }

    if (element.animation === "scale") {
      return (
        <rect
          x={element.x - (width * progress) / 2}
          y={element.y - (height * progress) / 2}
          width={width * progress}
          height={height * progress}
          fill="none"
          stroke={element.color}
          strokeWidth={element.stroke_width}
          opacity={progress}
          filter={`drop-shadow(0 0 10px ${element.color})`}
        />
      );
    }

    return (
      <rect
        x={element.x - width / 2}
        y={element.y - height / 2}
        width={width}
        height={height}
        fill="none"
        stroke={element.color}
        strokeWidth={element.stroke_width}
        opacity={progress}
        filter={`drop-shadow(0 0 10px ${element.color})`}
      />
    );
  }

  // LINE
  if (element.type === "line") {
    const [x2, y2] = element.data.split(",").map(parseFloat);

    if (element.animation === "draw") {
      const currentX2 = interpolate(progress, [0, 1], [element.x, x2]);
      const currentY2 = interpolate(progress, [0, 1], [element.y, y2]);

      return (
        <line
          x1={element.x}
          y1={element.y}
          x2={currentX2}
          y2={currentY2}
          stroke={element.color}
          strokeWidth={element.stroke_width}
          strokeLinecap="round"
          filter={`drop-shadow(0 0 8px ${element.color})`}
        />
      );
    }

    return (
      <line
        x1={element.x}
        y1={element.y}
        x2={x2}
        y2={y2}
        stroke={element.color}
        strokeWidth={element.stroke_width}
        strokeLinecap="round"
        opacity={progress}
        filter={`drop-shadow(0 0 8px ${element.color})`}
      />
    );
  }

  // PATH
  if (element.type === "path") {
    // --- START FIX: Dynamic Path Length ---
    const pathRef = React.useRef<SVGPathElement>(null);
    const [pathLength, setPathLength] = React.useState(0);

    React.useEffect(() => {
      if (pathRef.current) {
        // Measure the true length of the SVG path
        setPathLength(pathRef.current.getTotalLength());
      }
    }, [element.data]); // Re-measure if the path data ever changes

    if (element.animation === "draw") {
      // Use the DYNAMIC pathLength from state
      const dashOffset = pathLength * (1 - progress);

      return (
        <path
          ref={pathRef} // Add the ref here
          d={element.data}
          fill="none"
          stroke={element.color}
          strokeWidth={element.stroke_width}
          strokeDasharray={pathLength} // Use the state variable
          strokeDashoffset={dashOffset} // Use the calculated offset
          filter={`drop-shadow(0 0 10px ${element.color})`}
        />
      );
    }

    return (
      <path
        d={element.data}
        fill="none"
        stroke={element.color}
        strokeWidth={element.stroke_width}
        opacity={progress}
        filter={`drop-shadow(0 0 10px ${element.color})`}
      />
    );
  }

  // TEXT
  if (element.type === "text") {
    const y = interpolate(progress, [0, 1], [element.y + 20, element.y]);

    return (
      <text
        x={element.x}
        y={y}
        fill={element.color}
        fontSize={32}
        fontFamily={MANIM_FONT}
        textAnchor="middle"
        opacity={progress}
        filter="drop-shadow(0 2px 4px rgba(0,0,0,0.5))"
      >
        {element.data}
      </text>
    );
  }

  // EQUATION
  if (element.type === "equation") {
    const y = interpolate(progress, [0, 1], [element.y + 20, element.y]);

    return (
      <text
        x={element.x}
        y={y}
        fill={element.color}
        fontSize={48}
        fontFamily={MANIM_FONT}
        fontWeight={700}
        textAnchor="middle"
        opacity={progress}
        filter={`drop-shadow(0 0 15px ${element.color})`}
      >
        {element.data}
      </text>
    );
  }

  return null;
};
