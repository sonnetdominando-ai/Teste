import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

type AnimType = "fadeUp" | "fadeDown" | "fadeLeft" | "fadeRight" | "fadeIn" | "scale";

interface AnimatedTextProps {
  children: React.ReactNode;
  delay?: number;
  type?: AnimType;
  style?: React.CSSProperties;
  exitAt?: number;
}

export const AnimatedText: React.FC<AnimatedTextProps> = ({
  children,
  delay = 0,
  type = "fadeUp",
  style,
  exitAt,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delay);

  const progress = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 180, stiffness: 90, mass: 0.6 },
  });

  const opacity = interpolate(adjustedFrame, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  let translateX = 0;
  let translateY = 0;
  let scale = 1;

  switch (type) {
    case "fadeUp":
      translateY = interpolate(progress, [0, 1], [40, 0]);
      break;
    case "fadeDown":
      translateY = interpolate(progress, [0, 1], [-40, 0]);
      break;
    case "fadeLeft":
      translateX = interpolate(progress, [0, 1], [50, 0]);
      break;
    case "fadeRight":
      translateX = interpolate(progress, [0, 1], [-50, 0]);
      break;
    case "scale":
      scale = interpolate(progress, [0, 1], [0.85, 1]);
      break;
    case "fadeIn":
    default:
      break;
  }

  // Saída suave no fim da cena
  const exitOpacity =
    exitAt != null
      ? interpolate(frame, [exitAt, exitAt + 15], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 1;

  return (
    <div
      style={{
        opacity: opacity * exitOpacity,
        transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};
