import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BODY, BRAND, DISPLAY, fontFaces } from "./brand";

export type ShortConfig = {
  id: string;
  audio: string;
  durationInSeconds: number;
  stills: { image: string; from: number; to: number }[];
  captions: { at: number; until: number; text: string; em?: boolean }[];
};

/**
 * The vertical cut, for Shorts, Reels and TikTok.
 *
 * Not a crop of the landscape master. A 16:9 still cropped to 9:16 loses
 * two thirds of a slide that was designed edge to edge, so the still keeps
 * its own shape at full width and the rest of the height goes to type.
 *
 * Layout respects the phone: roughly the top 200px and bottom 380px of the
 * frame are covered by platform interface, so everything that has to be read
 * sits between them.
 */
const SAFE_TOP = 210;
const SAFE_BOTTOM = 390;

export const FinishOneShort: React.FC<{ config: ShortConfig }> = ({ config }) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.background }}>
      <style>{fontFaces}</style>
      <Audio src={staticFile(config.audio)} />

      <Backdrop />

      {config.stills.map((still, i) => {
        const from = Math.round(still.from * fps);
        const length = Math.round((still.to - still.from) * fps);
        return (
          <Sequence key={i} from={from} durationInFrames={length} layout="none">
            <Still image={still.image} length={length} />
          </Sequence>
        );
      })}

      <Captions captions={config.captions} stills={config.stills} />
      <Chrome />
    </AbsoluteFill>
  );
};

const Still: React.FC<{ image: string; length: number }> = ({ image, length }) => {
  const frame = useCurrentFrame();
  const fade = Math.min(
    interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" }),
    interpolate(frame, [length - 8, length], [1, 0], { extrapolateLeft: "clamp" })
  );
  const scale = interpolate(frame, [0, length], [1, 1.03], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity: fade }}>
      <div
        style={{
          position: "absolute",
          top: SAFE_TOP + 120,
          left: 0,
          width: 1080,
          height: 608,
          overflow: "hidden",
          borderTop: `5px solid ${BRAND.pink}`,
          borderBottom: `5px solid ${BRAND.pink}`,
        }}
      >
        <Img
          src={staticFile(image)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale})`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

/**
 * Burned-in captions. A Short is watched muted more often than not, so these
 * carry the script on their own. Each line is on screen for exactly as long
 * as it is spoken, which the measured alignment gives directly.
 */
const Captions: React.FC<{
  captions: ShortConfig["captions"];
  stills: ShortConfig["stills"];
}> = ({ captions, stills }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // With a still on screen the caption is a chip beneath it. Without one it
  // becomes the whole frame - a bottom caption over an empty vertical middle
  // reads as a missing asset rather than as a design.
  const hasStill = stills.some((s) => t >= s.from && t <= s.to);

  return (
    <>
      {captions.map((cap, i) => {
        // Hold the line a moment past the word, so a fast line does not
        // flash, but never past the next one.
        const next = captions[i + 1]?.at ?? cap.until + 0.6;
        const until = Math.min(cap.until + 0.45, next - 0.03);
        if (t < cap.at - 0.12 || t > until + 0.2) return null;

        const appear = spring({
          frame: Math.max(0, (t - cap.at) * fps),
          fps,
          config: { damping: 200, stiffness: 110, mass: 0.6 },
        });
        const out = interpolate(t, [until, until + 0.18], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        return (
          <div
            key={i}
            style={
              hasStill
                ? {
                    position: "absolute",
                    left: 0,
                    right: 0,
                    bottom: SAFE_BOTTOM + 90,
                    padding: "0 72px",
                    textAlign: "center",
                    opacity: Math.min(appear, out),
                    transform: `translateY(${interpolate(appear, [0, 1], [26, 0])}px)`,
                  }
                : {
                    position: "absolute",
                    left: 0,
                    right: 0,
                    top: SAFE_TOP,
                    bottom: SAFE_BOTTOM,
                    padding: "0 84px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    textAlign: "center",
                    opacity: Math.min(appear, out),
                    transform: `translateY(${interpolate(appear, [0, 1], [30, 0])}px)`,
                  }
            }
          >
            <span
              style={{
                display: "inline-block",
                padding: hasStill ? "18px 30px" : 0,
                backgroundColor: !hasStill
                  ? "transparent"
                  : cap.em
                  ? "rgba(255,20,147,0.14)"
                  : "rgba(14,11,31,0.82)",
                border: hasStill
                  ? `3px solid ${cap.em ? BRAND.pink : "rgba(46,39,84,0.9)"}`
                  : "none",
                fontFamily: cap.em ? DISPLAY : BODY,
                fontWeight: cap.em ? 700 : 600,
                fontSize: hasStill
                  ? sizeFor(cap.text, cap.em)
                  : sizeFor(cap.text, cap.em) * 1.5,
                lineHeight: 1.22,
                letterSpacing: cap.em ? 1 : 0.3,
                color: cap.em ? BRAND.pink : BRAND.text,
                textShadow: cap.em
                  ? "0 0 46px rgba(255,20,147,0.4), 0 3px 18px rgba(0,0,0,0.8)"
                  : "0 3px 18px rgba(0,0,0,0.8)",
              }}
            >
              {cap.text}
            </span>
          </div>
        );
      })}
    </>
  );
};

/** Keep the longest caption inside the safe width rather than trusting one size. */
function sizeFor(text: string, em?: boolean) {
  const fitted = 900 / (0.46 * Math.max(text.length / linesFor(text), 1));
  return Math.max(40, Math.min(em ? 66 : 72, fitted));
}

/** Long captions wrap; estimate how many rows so the size is not halved twice. */
function linesFor(text: string) {
  return text.length > 46 ? 2 : 1;
}

const Chrome: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: SAFE_TOP,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: DISPLAY,
          fontWeight: 700,
          fontSize: 30,
          letterSpacing: 11,
          color: BRAND.pink,
          textShadow: "0 0 34px rgba(255,20,147,0.5)",
        }}
      >
        {BRAND.wordmark}
      </div>

      <div
        style={{
          position: "absolute",
          bottom: SAFE_BOTTOM,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: BODY,
          fontWeight: 600,
          fontSize: 27,
          letterSpacing: 4,
          color: BRAND.muted,
        }}
      >
        THE 100-DAY AI FINISH LINE
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          bottom: 0,
          height: 8,
          width: `${(frame / durationInFrames) * 100}%`,
          background: `linear-gradient(90deg, ${BRAND.pink}, ${BRAND.pinkSoft})`,
        }}
      />
    </AbsoluteFill>
  );
};

const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const drift = Math.sin((frame / fps) * 0.3);

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.background }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at ${50 + drift * 8}% ${
            38 + drift * 5
          }%, rgba(255,20,147,0.24) 0%, rgba(255,20,147,0.06) 32%, rgba(14,11,31,0) 60%)`,
        }}
      />
    </AbsoluteFill>
  );
};
