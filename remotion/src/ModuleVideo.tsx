import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BRAND, fontFaces } from "./brand";
import { Chrome } from "./components/Chrome";
import { ScreenshotCard } from "./components/ScreenshotCard";
import { resolveSlides, type ModuleConfig, type ResolvedSlide } from "./types";

const FADE = 12;

const SlideFrame: React.FC<{
  slide: ResolvedSlide;
  config: ModuleConfig;
  total: number;
  durationInFrames: number;
}> = ({ slide, config, total, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade in only. Each slide is held FADE frames past its end so the next one
  // fades in on top of it; fading this one out too would dip to background at
  // every seam instead of cross-fading.
  const opacity = interpolate(frame, [0, FADE], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // A slow push-in keeps a still slide from feeling frozen over a long hold.
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.02], {
    extrapolateRight: "clamp",
  });

  const shots = slide.shots ?? [];
  const perShot = shots.length > 0 ? durationInFrames / shots.length : 0;

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.background, opacity }}>
      <AbsoluteFill style={{ transform: `scale(${scale})` }}>
        <Img
          src={staticFile(`${config.slidesDir}/${slide.image}`)}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
        />
      </AbsoluteFill>

      {shots.map((shot, i) => (
        <Sequence
          key={shot.src}
          from={Math.round(i * perShot)}
          durationInFrames={Math.round(perShot)}
          layout="none"
        >
          <ScreenshotCard
            src={`${config.shotsDir}/${shot.src}`}
            caption={shot.caption}
            position={i + 1}
            total={shots.length}
            outAt={Math.round(perShot) - 2}
          />
        </Sequence>
      ))}

      <Chrome
        index={slide.index}
        total={total}
        progress={(slide.index + frame / durationInFrames) / total}
      />
    </AbsoluteFill>
  );
};

export const ModuleVideo: React.FC<{ config: ModuleConfig }> = ({ config }) => {
  const { fps } = useVideoConfig();
  const slides = resolveSlides(config);

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.background }}>
      <style>{fontFaces}</style>
      <Audio src={staticFile(config.narration)} />

      {slides.map((slide) => {
        const from = Math.round(slide.start * fps);
        const duration = Math.max(1, Math.round((slide.end - slide.start) * fps));
        const isLast = slide.index === slides.length - 1;
        return (
          <Sequence
            key={slide.image}
            from={from}
            durationInFrames={isLast ? duration : duration + FADE}
          >
            <SlideFrame
              slide={slide}
              config={config}
              total={slides.length}
              durationInFrames={duration}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
