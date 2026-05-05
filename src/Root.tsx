import React from "react";
import { Composition } from "remotion";
import { AnclivepaVideo } from "./Video";
import { DURATIONS, FPS, HEIGHT, WIDTH } from "./constants";

const totalFrames = Object.values(DURATIONS).reduce((a, b) => a + b, 0);

export const Root: React.FC = () => {
  return (
    <Composition
      id="AnclivepaVideo"
      component={AnclivepaVideo}
      durationInFrames={totalFrames}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};
