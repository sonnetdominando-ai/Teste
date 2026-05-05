import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../constants";

interface LogoProps {
  delay?: number;
  size?: number;
  showTagline?: boolean;
}

const LogoPlaceholder: React.FC<{ size: number }> = ({ size }) => (
  <div
    style={{
      width: size,
      height: size * 0.45,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      border: `2px solid ${COLORS.gold}`,
      borderRadius: 8,
      padding: "12px 24px",
      gap: 6,
    }}
  >
    <div
      style={{
        fontFamily: "'Georgia', serif",
        fontSize: size * 0.11,
        fontWeight: 700,
        color: COLORS.gold,
        letterSpacing: 3,
        textTransform: "uppercase",
      }}
    >
      ANCLIVEPA
    </div>
    <div
      style={{
        fontFamily: "'Georgia', serif",
        fontSize: size * 0.065,
        color: COLORS.offWhite,
        letterSpacing: 6,
        textTransform: "uppercase",
      }}
    >
      RJ · FACULDADE
    </div>
  </div>
);

export const Logo: React.FC<LogoProps> = ({ delay = 0, size = 320, showTagline = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delay);

  const progress = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 200, stiffness: 80, mass: 0.8 },
  });

  const opacity = interpolate(adjustedFrame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(progress, [0, 1], [0.9, 1]);

  return (
    <div
      style={{
        opacity,
        transform: `scale(${scale})`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 16,
      }}
    >
      {/* Substitua pelo <Img> abaixo quando tiver o logo real:
          <Img src={staticFile("logo/logo.png")} style={{ width: size, height: "auto" }} />
      */}
      <LogoPlaceholder size={size} />

      {showTagline && (
        <div
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 20,
            color: COLORS.gray,
            letterSpacing: 3,
            textTransform: "uppercase",
          }}
        >
          Medicina Veterinária
        </div>
      )}
    </div>
  );
};
