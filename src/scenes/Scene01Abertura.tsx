import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { AnimatedText } from "../components/AnimatedText";
import { Logo } from "../components/Logo";
import { MediaBackground } from "../components/MediaBackground";
import { SceneWrapper } from "../components/SceneWrapper";
import { COLORS, GRADIENTS } from "../constants";

export const Scene01Abertura: React.FC = () => {
  const frame = useCurrentFrame();

  const lineWidth = interpolate(frame, [30, 70], [0, 200], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneWrapper
      background={
        <MediaBackground
          gradient={GRADIENTS.s1}
          // imageSrc="fotos/foto-01.jpg"   ← descomente quando tiver a foto
        />
      }
    >
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 72px",
          gap: 0,
        }}
      >
        {/* Logo no topo */}
        <div style={{ marginBottom: 80 }}>
          <Logo delay={5} size={300} />
        </div>

        {/* Linha divisória animada */}
        <div
          style={{
            width: lineWidth,
            height: 1.5,
            background: COLORS.gold,
            marginBottom: 48,
          }}
        />

        {/* Headline */}
        <AnimatedText
          delay={35}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 46,
            fontWeight: 300,
            color: COLORS.offWhite,
            lineHeight: 1.4,
            textAlign: "center",
            letterSpacing: 0.5,
          }}
        >
          "Na veterinária,
        </AnimatedText>

        <AnimatedText
          delay={50}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 46,
            fontWeight: 700,
            color: COLORS.white,
            lineHeight: 1.4,
            textAlign: "center",
            marginTop: 8,
          }}
        >
          teoria sozinha
        </AnimatedText>

        <AnimatedText
          delay={65}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 40,
            fontWeight: 300,
            color: COLORS.offWhite,
            lineHeight: 1.4,
            textAlign: "center",
            marginTop: 4,
            letterSpacing: 0.5,
          }}
        >
          não forma segurança."
        </AnimatedText>

        {/* Sub */}
        <AnimatedText
          delay={90}
          type="fadeIn"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 22,
            color: COLORS.gold,
            letterSpacing: 4,
            textTransform: "uppercase",
            marginTop: 48,
          }}
        >
          Pós-Graduação Prática
        </AnimatedText>
      </AbsoluteFill>
    </SceneWrapper>
  );
};
