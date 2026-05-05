import React from "react";
import { AbsoluteFill } from "remotion";
import { AnimatedText } from "../components/AnimatedText";
import { MediaBackground } from "../components/MediaBackground";
import { SceneWrapper } from "../components/SceneWrapper";
import { COLORS, GRADIENTS } from "../constants";

export const Scene03Cirurgia: React.FC = () => {
  return (
    <SceneWrapper
      background={
        <MediaBackground
          gradient={GRADIENTS.s3}
          // videoSrc="videos/video-01.mp4"  ← descomente quando tiver o vídeo
          // imageSrc="fotos/foto-02.jpg"
        />
      }
    >
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          padding: "0 72px 140px",
        }}
      >
        {/* Specialty badge */}
        <AnimatedText
          delay={10}
          type="fadeLeft"
          style={{
            display: "inline-block",
            fontFamily: "'Georgia', serif",
            fontSize: 16,
            color: COLORS.bgDark,
            background: COLORS.gold,
            letterSpacing: 4,
            textTransform: "uppercase",
            padding: "6px 20px",
            marginBottom: 28,
            alignSelf: "flex-start",
          }}
        >
          Especialidade
        </AnimatedText>

        <AnimatedText
          delay={20}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 72,
            fontWeight: 700,
            color: COLORS.white,
            lineHeight: 1.1,
            marginBottom: 4,
          }}
        >
          Cirurgia
        </AnimatedText>

        <AnimatedText
          delay={30}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 40,
            fontWeight: 300,
            color: COLORS.gold,
            letterSpacing: 2,
            marginBottom: 40,
          }}
        >
          Veterinária
        </AnimatedText>

        {/* Linha */}
        <div style={{ width: 50, height: 1.5, background: COLORS.gold, marginBottom: 36 }} />

        <AnimatedText
          delay={55}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 30,
            fontWeight: 300,
            color: COLORS.offWhite,
            lineHeight: 1.6,
          }}
        >
          Mais do que saber a técnica,
        </AnimatedText>

        <AnimatedText
          delay={70}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 30,
            fontWeight: 600,
            color: COLORS.white,
            lineHeight: 1.6,
          }}
        >
          é entender quando, como
        </AnimatedText>

        <AnimatedText
          delay={85}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 30,
            fontWeight: 300,
            color: COLORS.offWhite,
            lineHeight: 1.6,
          }}
        >
          e por que aplicar.
        </AnimatedText>
      </AbsoluteFill>
    </SceneWrapper>
  );
};
