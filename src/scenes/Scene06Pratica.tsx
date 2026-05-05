import React from "react";
import { AbsoluteFill } from "remotion";
import { AnimatedText } from "../components/AnimatedText";
import { MediaBackground } from "../components/MediaBackground";
import { SceneWrapper } from "../components/SceneWrapper";
import { COLORS, GRADIENTS } from "../constants";

const BulletItem: React.FC<{ text: string; delay: number }> = ({ text, delay }) => (
  <AnimatedText
    delay={delay}
    type="fadeLeft"
    style={{
      display: "flex",
      alignItems: "center",
      gap: 16,
      fontFamily: "'Georgia', serif",
      fontSize: 32,
      fontWeight: 300,
      color: COLORS.offWhite,
      lineHeight: 1.5,
    }}
  >
    <span
      style={{
        width: 8,
        height: 8,
        borderRadius: "50%",
        background: COLORS.gold,
        flexShrink: 0,
        display: "inline-block",
      }}
    />
    {text}
  </AnimatedText>
);

export const Scene06Pratica: React.FC = () => {
  return (
    <SceneWrapper
      background={
        <MediaBackground
          gradient={GRADIENTS.s6}
          // videoSrc="videos/video-02.mp4"  ← descomente quando tiver o vídeo
          // imageSrc="fotos/foto-05.jpg"
        />
      }
    >
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "0 72px",
        }}
      >
        <AnimatedText
          delay={10}
          type="fadeIn"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 22,
            color: COLORS.gold,
            letterSpacing: 5,
            textTransform: "uppercase",
            marginBottom: 40,
          }}
        >
          Metodologia
        </AnimatedText>

        <AnimatedText
          delay={20}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 52,
            fontWeight: 700,
            color: COLORS.white,
            lineHeight: 1.2,
            marginBottom: 16,
          }}
        >
          Aqui o aluno
        </AnimatedText>

        <AnimatedText
          delay={35}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 40,
            fontWeight: 300,
            color: COLORS.gold,
            lineHeight: 1.4,
            marginBottom: 48,
          }}
        >
          participa de verdade.
        </AnimatedText>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 20,
          }}
        >
          <BulletItem text="Pratica com orientação direta" delay={55} />
          <BulletItem text="Corrige em tempo real" delay={70} />
          <BulletItem text="Evolui com cada caso clínico" delay={85} />
          <BulletItem text="Professor presente, não distante" delay={100} />
        </div>
      </AbsoluteFill>
    </SceneWrapper>
  );
};
