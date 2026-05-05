import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../constants";

interface CTABlockProps {
  delay?: number;
}

const Line: React.FC<{
  text: string;
  delay: number;
  fontSize: number;
  color: string;
  weight?: number;
  letterSpacing?: number;
}> = ({ text, delay, fontSize, color, weight = 400, letterSpacing = 0.5 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delay);
  const progress = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 200, stiffness: 100, mass: 0.5 },
  });

  const opacity = interpolate(adjustedFrame, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(progress, [0, 1], [24, 0]);

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${translateY}px)`,
        fontFamily: "'Georgia', serif",
        fontSize,
        fontWeight: weight,
        color,
        letterSpacing,
        textAlign: "center",
      }}
    >
      {text}
    </div>
  );
};

export const CTABlock: React.FC<CTABlockProps> = ({ delay = 0 }) => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 20,
        width: "100%",
        padding: "0 60px",
      }}
    >
      <Line
        text="Quer evoluir na prática?"
        delay={delay}
        fontSize={44}
        color={COLORS.offWhite}
        weight={300}
        letterSpacing={1}
      />

      <div style={{ width: 60, height: 2, background: COLORS.gold, marginTop: 8 }} />

      <Line
        text="Inscrições abertas"
        delay={delay + 15}
        fontSize={56}
        color={COLORS.gold}
        weight={700}
        letterSpacing={2}
      />

      <div
        style={{
          height: 24,
        }}
      />

      <Line
        text="ANCLIVEPA RJ — FACULDADE"
        delay={delay + 30}
        fontSize={32}
        color={COLORS.offWhite}
        weight={600}
        letterSpacing={4}
      />

      <Line
        text="WhatsApp: (21) 97285-2428"
        delay={delay + 45}
        fontSize={34}
        color={COLORS.gold}
        weight={400}
        letterSpacing={1.5}
      />

      <Line
        text="Campus · Rio de Janeiro"
        delay={delay + 60}
        fontSize={28}
        color={COLORS.gray}
        weight={300}
        letterSpacing={3}
      />
    </div>
  );
};
