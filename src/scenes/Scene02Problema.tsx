import React from "react";
import { AbsoluteFill } from "remotion";
import { AnimatedText } from "../components/AnimatedText";
import { MediaBackground } from "../components/MediaBackground";
import { SceneWrapper } from "../components/SceneWrapper";
import { COLORS, GRADIENTS } from "../constants";

export const Scene02Problema: React.FC = () => {
  return (
    <SceneWrapper
      background={
        <MediaBackground
          gradient={GRADIENTS.s2}
          // imageSrc="fotos/foto-02.jpg"   ← descomente quando tiver a foto
        />
      }
    >
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "0 72px",
          gap: 0,
        }}
      >
        {/* Label de seção */}
        <AnimatedText
          delay={10}
          type="fadeLeft"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 18,
            color: COLORS.gold,
            letterSpacing: 5,
            textTransform: "uppercase",
            marginBottom: 32,
          }}
        >
          O Desafio
        </AnimatedText>

        <AnimatedText
          delay={20}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 52,
            fontWeight: 700,
            color: COLORS.white,
            lineHeight: 1.25,
            marginBottom: 16,
          }}
        >
          Na prática,
        </AnimatedText>

        <AnimatedText
          delay={35}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 44,
            fontWeight: 300,
            color: COLORS.offWhite,
            lineHeight: 1.4,
            marginBottom: 8,
          }}
        >
          o aluno precisa
        </AnimatedText>

        <AnimatedText
          delay={50}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 44,
            fontWeight: 600,
            color: COLORS.gold,
            lineHeight: 1.4,
          }}
        >
          decidir, executar
        </AnimatedText>

        <AnimatedText
          delay={65}
          type="fadeUp"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 44,
            fontWeight: 300,
            color: COLORS.offWhite,
            lineHeight: 1.4,
          }}
        >
          e evoluir.
        </AnimatedText>

        {/* Linha separadora */}
        <div
          style={{
            width: 60,
            height: 2,
            background: COLORS.gold,
            marginTop: 48,
            opacity: 0.8,
          }}
        />

        <AnimatedText
          delay={100}
          type="fadeIn"
          style={{
            fontFamily: "'Georgia', serif",
            fontSize: 24,
            fontWeight: 300,
            color: COLORS.gray,
            lineHeight: 1.6,
            marginTop: 32,
          }}
        >
          É para isso que a pós da{"\n"}
          <span style={{ color: COLORS.offWhite }}>Anclivepa RJ</span> foi criada.
        </AnimatedText>
      </AbsoluteFill>
    </SceneWrapper>
  );
};
