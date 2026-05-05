import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

interface SceneWrapperProps {
  children: React.ReactNode;
  background: React.ReactNode;
  fadeInDuration?: number;
  fadeOutDuration?: number;
}

export const SceneWrapper: React.FC<SceneWrapperProps> = ({
  children,
  background,
  fadeInDuration = 18,
  fadeOutDuration = 18,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, fadeInDuration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const fadeOut = interpolate(
    frame,
    [durationInFrames - fadeOutDuration, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill>{background}</AbsoluteFill>
      <AbsoluteFill>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};
