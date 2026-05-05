import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { CTABlock } from "../components/CTABlock";
import { Logo } from "../components/Logo";
import { MediaBackground } from "../components/MediaBackground";
import { SceneWrapper } from "../components/SceneWrapper";
import { COLORS, GRADIENTS } from "../constants";

export const Scene08CTA: React.FC = () => {
  const frame = useCurrentFrame();

  const glowOpacity = interpolate(frame, [30, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneWrapper
      background={
        <MediaBackground
          gradient={GRADIENTS.s8}
          kenBurns={false}
        />
      }
    >
      {/* Glow dourado de fundo */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at 50% 55%, rgba(201,168,76,0.12) 0%, transparent 60%)`,
          opacity: glowOpacity,
        }}
      />

      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 56px",
          gap: 0,
        }}
      >
        {/* Logo no topo */}
        <div style={{ marginBottom: 60 }}>
          <Logo delay={10} size={260} />
        </div>

        {/* Linha divisória */}
        <div
          style={{
            width: interpolate(frame, [30, 70], [0, 120], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            height: 1.5,
            background: COLORS.gold,
            marginBottom: 56,
          }}
        />

        {/* Bloco CTA */}
        <CTABlock delay={40} />

        {/* Rodapé */}
        <div
          style={{
            position: "absolute",
            bottom: 80,
            left: 0,
            right: 0,
            display: "flex",
            justifyContent: "center",
            opacity: interpolate(frame, [120, 150], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div
            style={{
              fontFamily: "'Georgia', serif",
              fontSize: 16,
              color: COLORS.gray,
              letterSpacing: 3,
              textTransform: "uppercase",
            }}
          >
            anclivepa-rj.com.br
          </div>
        </div>
      </AbsoluteFill>
    </SceneWrapper>
  );
};
