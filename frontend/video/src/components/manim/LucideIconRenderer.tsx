import React from "react";
// THIS LINE IS NOW FIXED
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import * as LucideIcons from "lucide-react";
import type { SVGElement } from "../../types";

// Type assertion for dynamic icon access
type IconName = keyof typeof LucideIcons;

interface Props {
  element: SVGElement;
}

// This helper component manages the state for drawing a single <path>
const AnimatingPath: React.FC<{
  d: string;
  progress: number;
  color: string;
  strokeWidth: number;
}> = ({ d, progress, color, strokeWidth }) => {
  const ref = React.useRef<SVGPathElement>(null);
  const [length, setLength] = React.useState(0);

  // Use useLayoutEffect to measure the path length before the browser paints
  React.useLayoutEffect(() => {
    if (ref.current) {
      setLength(ref.current.getTotalLength());
    }
  }, [d]); // Re-measure if the path data changes

  // Calculate the dash offset
  const offset = length * (1 - progress);

  return (
    <path
      ref={ref}
      d={d}
      stroke={color}
      strokeWidth={strokeWidth}
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
      filter={`drop-shadow(0 0 10px ${color})`}
      strokeDasharray={length} // Set the dash array to the total length
      strokeDashoffset={offset} // Animate the offset
    />
  );
};

// This function finds all path 'd' strings from the icon
const getAllPaths = (iconName: IconName, size: number): string[] => {
  const IconComponent = LucideIcons[iconName] as React.ElementType;
  if (!IconComponent) {
    console.warn(`Lucide icon "${iconName}" not found.`);
    return [];
  }

  const { renderToStaticMarkup } = require("react-dom/server");
  const stringSvg = renderToStaticMarkup(
    React.createElement(IconComponent, { size, color: "white" })
  );

  const pathRegex = /d="([^"]*)"/g;
  const paths: string[] = [];
  let match;

  while ((match = pathRegex.exec(stringSvg)) !== null) {
    paths.push(match[1]);
  }

  if (paths.length === 0) {
    console.warn(`No <path> elements found for icon "${iconName}".`);
  }

  return paths;
};

// MAIN COMPONENT
export const LucideIconRenderer: React.FC<Props> = ({ element }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const [iconName, sizeStr] = element.data.split(",");
  const size = parseFloat(sizeStr);
  const iconKey = iconName as IconName;

  const allPaths = React.useMemo(
    () => getAllPaths(iconKey, size),
    [iconKey, size]
  );

  const progress = spring({
    frame: frame - element.delay,
    fps,
    config: { damping: 100 },
  });

  // --- THE SCALING FIX ---
  // Lucide icons are in a 24x24 viewport.
  const NATIVE_VIEWBOX_SIZE = 24;
  const NATIVE_VIEWBOX_CENTER = NATIVE_VIEWBOX_SIZE / 2;
  const scaleFactor = size / NATIVE_VIEWBOX_SIZE;

  // This transform moves to the (x,y) coord, scales up, and centers the 24x24 box
  const baseTransform = `translate(${element.x}, ${element.y}) scale(${scaleFactor}) translate(-${NATIVE_VIEWBOX_CENTER}, -${NATIVE_VIEWBOX_CENTER})`;
  // --- END FIX ---

  // Handle "draw" animation
  if (element.animation === "draw") {
    return (
      <g transform={baseTransform} opacity={progress > 0.05 ? 1 : 0}>
        {allPaths.map((path, i) => (
          <AnimatingPath
            key={i}
            d={path}
            progress={progress}
            color={element.color}
            // We must "thin" the stroke by the same amount we scale up
            strokeWidth={element.stroke_width / scaleFactor}
          />
        ))}
      </g>
    );
  }

  // Default: "fade" or "scale" animation
  const animatedScale = element.animation === "scale" ? progress : 1;
  const opacity = progress;

  // Combine the base scale with the animation scale
  const combinedScaleFactor = scaleFactor * animatedScale;

  const transform = `translate(${element.x}, ${element.y}) scale(${combinedScaleFactor}) translate(-${NATIVE_VIEWBOX_CENTER}, -${NATIVE_VIEWBOX_CENTER})`;

  return (
    <g transform={transform} opacity={opacity}>
      {allPaths.map((path, i) => (
        <path
          key={i}
          d={path}
          stroke={element.color}
          // "Thin" the stroke here too
          strokeWidth={element.stroke_width / scaleFactor}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter={`drop-shadow(0 0 10px ${element.color})`}
        />
      ))}
    </g>
  );
};
