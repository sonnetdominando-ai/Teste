import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { AnimatedText } from "../components/AnimatedText";
import { MediaBackground } from "../components/MediaBackground";
import { SceneWrapper } from "../components/SceneWrapper";
import { COLORS, GRADIENTS } from "../constants";

const DifCard: React.FC<{ icon: string; title: string; delay: number }> = ({
  icon,
  title,
  delay,
}) => (
  <AnimatedText
    delay={delay}
    type="fadeUp"
    style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: 10,
      padding: "28px 20px",
      border: `1px solid rgba(201,168,76,0.3)`,
      borderRadius: 8,
      flex: 1,
      minWidth: 0,
    }}
  >
    <div style={{ fontSize: 36 }}>{icon}</div>
    <div
      style={{
        fontFamily: "'Georgia', serif",
        fontSize: 20,
        fontWeight: 600,
        color: COLORS.offWhite,
        textAlign: "center",
        lineHeight: 1.3,
      }}
    >
      {title}
    </div>
  </AnimatedText>
);

export const Scene07Diferencial: React.FC = () => {
  const frame = useCurrentFrame();

  const lineWidth = interpolate(frame, [20, 70], [0, 160], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneWrapper
      background={
        <MediaBackground
          gradient={GRADIENTS.s7}
        />
      }
    >
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "0 64px",
          gap: 0,
        }}
      >
        <AnimatedText
          delay={10}
          type="fadeIn"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 20,
            color: COLORS.gold,
            letterSpacing: 5,
            textTransform: "uppercase",
            marginBottom: 32,
          }}
        >
          Por que a Anclivepa RJ?
        </AnimatedText>

        <AnimatedText
          delay={20}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 56,
            fontWeight: 700,
            color: COLORS.white,
            lineHeight: 1.15,
          }}
        >
          O diferencial
        </AnimatedText>

        <AnimatedText
          delay={35}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 44,
            fontWeight: 300,
            color: COLORS.gold,
            lineHeight: 1.3,
            marginBottom: 48,
          }}
        >
          que forma profissionais.
        </AnimatedText>

        <div
          style={{
            width: lineWidth,
            height: 1.5,
            background: COLORS.gold,
            marginBottom: 48,
          }}
        />

        {/* Cards diferenciais */}
        <div style={{ display: "flex", gap: 16, marginBottom: 40 }}>
          <DifCard icon="🎓" title="Aulas presenciais" delay={60} />
          <DifCard icon="🔬" title="Casos clínicos reais" delay={75} />
        </div>
        <div style={{ display: "flex", gap: 16 }}>
          <DifCard icon="🏥" title="Vivência real" delay={90} />
          <DifCard icon="👨‍⚕️" title="Professores experientes" delay={105} />
        </div>

        <AnimatedText
          delay={140}
          type="fadeIn"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 26,
            fontWeight: 300,
            color: COLORS.gray,
            lineHeight: 1.5,
            marginTop: 48,
            textAlign: "center",
          }}
        >
          Formação que prepara para o real.
        </AnimatedText>
      </AbsoluteFill>
    </SceneWrapper>
  );
};
