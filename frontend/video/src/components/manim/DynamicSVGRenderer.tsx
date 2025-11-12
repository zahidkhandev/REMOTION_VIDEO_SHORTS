import React from "react";
import { spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import type { SVGElement } from "../../types";
import { MANIM_FONT } from "./ManimBackground";
import { LucideIconRenderer } from "./LucideIconRenderer"; // <-- 1. IMPORT NEW COMPONENT

interface Props {
  element: SVGElement;
}

// A new hook to measure the size of an SVG <text> element
function useMeasure() {
  const [box, setBox] = React.useState<SVGRect | null>(null);
  const ref = React.useCallback((node: SVGTextElement | null) => {
    if (node) {
      requestAnimationFrame(() => {
        setBox(node.getBBox());
      });
    }
  }, []);
  return [box, ref] as const;
}

export const DynamicSVGRenderer: React.FC<Props> = ({ element }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const [box, textRef] = useMeasure();

  const progress = spring({
    frame: frame - element.delay,
    fps,
    config: { damping: 100 },
  });

  // --- *** NEW LUCIDE ICON LOGIC *** ---
  // 2. ADD THIS BLOCK
  if (element.type === "lucide_icon") {
    // We pass the whole element down to the new renderer,
    // which will handle parsing the data and all animations.
    return <LucideIconRenderer element={element} />;
  }
  // --- *** END NEW LOGIC *** ---

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

    // Default/Fade animation
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
          rx={8}
          ry={8}
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
          rx={8}
          ry={8}
        />
      );
    }
    // Default/Fade
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
        rx={8}
        ry={8}
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

    // Default/Fade animation
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
    const pathRef = React.useRef<SVGPathElement>(null);
    const [pathLength, setPathLength] = React.useState(0);

    React.useEffect(() => {
      if (pathRef.current) {
        setPathLength(pathRef.current.getTotalLength());
      }
    }, [element.data]);

    if (element.animation === "draw") {
      const dashOffset = pathLength * (1 - progress);

      return (
        <path
          ref={pathRef}
          d={element.data}
          fill="none"
          stroke={element.color}
          strokeWidth={element.stroke_width}
          strokeDasharray={pathLength}
          strokeDashoffset={dashOffset}
          filter={`drop-shadow(0 0 10px ${element.color})`}
        />
      );
    }

    // Default/Fade animation
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
    const hasBox = element.stroke_width > 0;
    const groupOpacity = progress;
    const textY = interpolate(progress, [0, 1], [element.y + 20, element.y]);

    return (
      <g opacity={groupOpacity}>
        {hasBox && box && (
          <rect
            x={box.x - 30}
            y={box.y - 30}
            width={box.width + 60}
            height={box.height + 60}
            fill="none"
            stroke={element.color}
            strokeWidth={element.stroke_width}
            filter={`drop-shadow(0 0 10px ${element.color})`}
            rx={8}
            ry={8}
          />
        )}
        <text
          ref={textRef}
          x={element.x}
          y={textY}
          fill={hasBox ? element.color : "#FFFFFF"}
          fontSize={32}
          fontFamily={MANIM_FONT}
          textAnchor="middle"
          dominantBaseline="central"
          filter="drop-shadow(0 2px 4px rgba(0,0,0,0.5))"
        >
          {element.data}
        </text>
      </g>
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
        dominantBaseline="central"
        opacity={progress}
        filter={`drop-shadow(0 0 15px ${element.color})`}
      >
        {element.data}
      </text>
    );
  }

  return null;
};
