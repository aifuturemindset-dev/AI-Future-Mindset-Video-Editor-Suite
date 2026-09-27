import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BODY, BRAND, DISPLAY, fontFaces } from "./brand";
import { BrandChrome } from "./components/BrandChrome";
import { KineticText, type Beat } from "./components/KineticText";

export type Scene =
  | {
      kind: "slide";
      image: string;
      from: number;
      to: number;
      say?: string;
      /** The animated version of this slide, when one exists. */
      video?: string;
      /** Still of the animation's last frame, held once the clip ends. */
      videoLast?: string;
      /** Seconds of animation available. */
      videoSeconds?: number;
    }
  | { kind: "text"; from: number; to: number; beats: Beat[] }
  | { kind: "end"; from: number; to: number; beats: Beat[] };

export type FinishOneConfig = {
  id: string;
  audio: string;
  durationInSeconds: number;
  scenes: Scene[];
};

/** Frames of overlap between scenes. Short enough to feel like a cut. */
const FADE = 9;

/**
 * "I Stopped Waiting to Feel Ready."
 *
 * Twelve storyboard stills carry the beats they were designed for, and the
 * narration between them runs as animated type. Every cue time comes from a
 * measured alignment of the script against the recording, so the visuals sit
 * on the sentences they belong to rather than on an even division of the
 * runtime.
 *
 * Scenes overlap by FADE frames and each fades in over whatever is beneath
 * it. Fading both at once would dip to the background colour between every
 * scene, which reads as a fault rather than a transition.
 */
export const FinishOne: React.FC<{ config: FinishOneConfig }> = ({ config }) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.background }}>
      <style>{fontFaces}</style>
      <Audio src={staticFile(config.audio)} />

      {config.scenes.map((scene, i) => {
        const from = Math.round(scene.from * fps);
        const length = Math.round((scene.to - scene.from) * fps);
        return (
          <Sequence
            key={i}
            from={from}
            durationInFrames={length + FADE}
            layout="none"
          >
            <FadeIn skip={i === 0}>
              {scene.kind === "slide" ? (
                <SlideScene scene={scene} length={length} />
              ) : scene.kind === "end" ? (
                <EndScene beats={scene.beats} from={scene.from} length={length} />
              ) : (
                <KineticText beats={scene.beats} sceneFrom={scene.from} />
              )}
            </FadeIn>
          </Sequence>
        );
      })}

      <BrandChrome />
    </AbsoluteFill>
  );
};

const FadeIn: React.FC<{ skip?: boolean; children: React.ReactNode }> = ({
  skip,
  children,
}) => {
  const frame = useCurrentFrame();
  const opacity = skip
    ? 1
    : interpolate(frame, [0, FADE], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
};

/**
 * A storyboard slide.
 *
 * Where an animated version exists it plays, slowed to cover the scene, with
 * its own last frame underneath so a scene longer than the clip holds instead
 * of cutting out. The clip is muted: the narration is the audio.
 *
 * Where there is no animation it falls back to the still, with a small push.
 * The push stays small on purpose - these are designed slides with type near
 * the edges, and more would crop it.
 */
const SlideScene: React.FC<{
  scene: Extract<Scene, { kind: "slide" }>;
  length: number;
}> = ({ scene, length }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (scene.video) {
    const available = scene.videoSeconds ?? 10;
    const sceneSeconds = (length + FADE) / fps;
    // Stretch the clip toward the scene length, but never so far that the
    // motion reads as slow-motion; whatever is left holds on the last frame.
    const rate = Math.min(1, Math.max(0.6, available / sceneSeconds));
    const playable = Math.round((available / rate) * fps);

    return (
      <AbsoluteFill style={{ backgroundColor: BRAND.background, overflow: "hidden" }}>
        {scene.videoLast ? (
          <Img
            src={staticFile(scene.videoLast)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : null}
        <Sequence durationInFrames={playable} layout="none">
          <OffthreadVideo
            src={staticFile(scene.video)}
            playbackRate={rate}
            muted
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </Sequence>
      </AbsoluteFill>
    );
  }

  const scale = interpolate(frame, [0, length + FADE], [1, 1.028], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.background, overflow: "hidden" }}>
      <Img
        src={staticFile(scene.image)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
        }}
      />
    </AbsoluteFill>
  );
};

/** The closing lines, then the wordmark alone. */
const EndScene: React.FC<{ beats: Beat[]; from: number; length: number }> = ({
  beats,
  from,
  length,
}) => {
  const frame = useCurrentFrame();
  const plate = interpolate(frame, [length - 58, length - 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ opacity: 1 - plate }}>
        <KineticText beats={beats} sceneFrom={from} />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          opacity: plate,
          backgroundColor: BRAND.background,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div
          style={{
            fontFamily: DISPLAY,
            fontWeight: 700,
            fontSize: 74,
            letterSpacing: 16,
            color: BRAND.pink,
            textShadow: "0 0 60px rgba(255,20,147,0.45)",
          }}
        >
          {BRAND.wordmark}
        </div>
        <div
          style={{
            marginTop: 26,
            fontFamily: BODY,
            fontWeight: 600,
            fontSize: 36,
            letterSpacing: 5,
            color: BRAND.muted,
          }}
        >
          By Day 30, I will have built ______
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
