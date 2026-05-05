import React from "react";
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS } from "../constants";

interface MediaBackgroundProps {
  gradient: string;
  imageSrc?: string;
  videoSrc?: string;
  overlay?: string;
  kenBurns?: boolean;
}

const GradientBg: React.FC<{ gradient: string; overlay: string }> = ({
  gradient,
  overlay,
}) => (
  <AbsoluteFill style={{ background: gradient }}>
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse at 50% 30%, rgba(201,168,76,0.06) 0%, transparent 65%)",
      }}
    />
    <AbsoluteFill style={{ background: overlay }} />
  </AbsoluteFill>
);

export const MediaBackground: React.FC<MediaBackgroundProps> = ({
  gradient,
  imageSrc,
  videoSrc,
  overlay = COLORS.overlay,
  kenBurns = true,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const scale = kenBurns
    ? interpolate(frame, [0, durationInFrames], [1.0, 1.06], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 1;

  if (videoSrc) {
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ transform: `scale(${scale})` }}>
          <OffthreadVideo
            src={staticFile(videoSrc)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </AbsoluteFill>
        <AbsoluteFill style={{ background: overlay }} />
      </AbsoluteFill>
    );
  }

  if (imageSrc) {
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{ transform: `scale(${scale})` }}>
          <Img
            src={staticFile(imageSrc)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </AbsoluteFill>
        <AbsoluteFill style={{ background: overlay }} />
      </AbsoluteFill>
    );
  }

  return <GradientBg gradient={gradient} overlay="transparent" />;
};
