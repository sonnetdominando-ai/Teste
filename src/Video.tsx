import React from "react";
import { AbsoluteFill, Audio, Series, staticFile } from "remotion";
import { COLORS, DURATIONS } from "./constants";
import { Scene01Abertura } from "./scenes/Scene01Abertura";
import { Scene02Problema } from "./scenes/Scene02Problema";
import { Scene03Cirurgia } from "./scenes/Scene03Cirurgia";
import { Scene04Cardiologia } from "./scenes/Scene04Cardiologia";
import { Scene05Oftalmologia } from "./scenes/Scene05Oftalmologia";
import { Scene06Pratica } from "./scenes/Scene06Pratica";
import { Scene07Diferencial } from "./scenes/Scene07Diferencial";
import { Scene08CTA } from "./scenes/Scene08CTA";

export const AnclivepaVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bgDark }}>
      {/*
        Para adicionar trilha sonora, descomente a linha abaixo
        e coloque o arquivo em /assets/audio/trilha.mp3
      */}
      {/* <Audio src={staticFile("audio/trilha.mp3")} volume={0.35} /> */}

      <Series>
        <Series.Sequence durationInFrames={DURATIONS.s1}>
          <Scene01Abertura />
        </Series.Sequence>

        <Series.Sequence durationInFrames={DURATIONS.s2}>
          <Scene02Problema />
        </Series.Sequence>

        <Series.Sequence durationInFrames={DURATIONS.s3}>
          <Scene03Cirurgia />
        </Series.Sequence>

        <Series.Sequence durationInFrames={DURATIONS.s4}>
          <Scene04Cardiologia />
        </Series.Sequence>

        <Series.Sequence durationInFrames={DURATIONS.s5}>
          <Scene05Oftalmologia />
        </Series.Sequence>

        <Series.Sequence durationInFrames={DURATIONS.s6}>
          <Scene06Pratica />
        </Series.Sequence>

        <Series.Sequence durationInFrames={DURATIONS.s7}>
          <Scene07Diferencial />
        </Series.Sequence>

        <Series.Sequence durationInFrames={DURATIONS.s8}>
          <Scene08CTA />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
