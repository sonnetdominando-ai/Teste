import React from "react";
import { AbsoluteFill } from "remotion";
import { AnimatedText } from "../components/AnimatedText";
import { MediaBackground } from "../components/MediaBackground";
import { SceneWrapper } from "../components/SceneWrapper";
import { COLORS, GRADIENTS } from "../constants";

export const Scene05Oftalmologia: React.FC = () => {
  return (
    <SceneWrapper
      background={
        <MediaBackground
          gradient={GRADIENTS.s5}
          // imageSrc="fotos/foto-04.jpg"  ← descomente quando tiver a foto
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
          Oftalmologia
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

        <div style={{ width: 50, height: 1.5, background: COLORS.gold, marginBottom: 36 }} />

        <AnimatedText
          delay={55}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 42,
            fontWeight: 700,
            color: COLORS.white,
            lineHeight: 1.3,
          }}
        >
          "Um detalhe
        </AnimatedText>

        <AnimatedText
          delay={70}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 42,
            fontWeight: 300,
            color: COLORS.offWhite,
            lineHeight: 1.3,
          }}
        >
          pode mudar tudo."
        </AnimatedText>
      </AbsoluteFill>
    </SceneWrapper>
  );
};
