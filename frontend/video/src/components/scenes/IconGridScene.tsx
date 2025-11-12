// frontend/video/src/components/scenes/IconGridScene.tsx (NEW FILE)

import React from "react";
import { AbsoluteFill } from "remotion";
import { motion } from "framer-motion";
import { Rocket, Database, BrainCircuit } from "lucide-react"; // Real icons!
import { MANIM_FONT } from "../manim/ManimBackground";

// 1. Map string names from AI to actual icon components
const iconMap = {
  Rocket: Rocket,
  Database: Database,
  BrainCircuit: BrainCircuit,
  // Add more icons here
};

// 2. Define the props structure the AI must provide
interface IconProps {
  type: "icon";
  name: keyof typeof iconMap; // AI must provide a name from iconMap
  label: string;
}

interface Props {
  props: IconProps[]; // Expects an array of icon props
}

// 3. Framer Motion animation variants
const gridVariant = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2, // Animate children one by one
    },
  },
};

const itemVariant = {
  hidden: { y: 20, opacity: 0 },
  visible: { y: 0, opacity: 1 },
};

export const IconGridScene: React.FC<Props> = ({ props }) => {
  return (
    <AbsoluteFill
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <motion.div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)", // Smart layout!
          gap: "40px",
          width: "80%",
        }}
        variants={gridVariant}
        initial="hidden"
        animate="visible"
      >
        {props.map((item) => {
          const IconComponent = iconMap[item.name] || BrainCircuit; // Fallback icon
          return (
            <motion.div
              key={item.label}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "20px",
              }}
              variants={itemVariant}
            >
              <IconComponent color="#6B9BD1" size={80} />
              <span
                style={{
                  fontFamily: MANIM_FONT,
                  fontSize: 32,
                  color: "#FFFFFF",
                  textAlign: "center",
                }}
              >
                {item.label}
              </span>
            </motion.div>
          );
        })}
      </motion.div>
    </AbsoluteFill>
  );
};
