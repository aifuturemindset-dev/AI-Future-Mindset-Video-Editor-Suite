import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BODY, BRAND, DISPLAY } from "../brand";

export type Beat = {
  /** Second in the finished video where the narration reaches this beat. */
  at: number;
  lines: string[];
  /** Carries the argument - set in the display face, in brand pink. */
  em?: boolean;
};

/**
 * The narration between stills, set as type.
 *
 * One beat holds the screen at a time and the next crosses over it, rather
 * than lines stacking up a page. The script is written in short spoken
 * clauses, so a beat is usually one or two lines and the cut rate carries
 * the rhythm of the read.
 */
export const KineticText: React.FC<{ beats: Beat[]; sceneFrom: number }> = ({
  beats,
  sceneFrom,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = sceneFrom + frame / fps;

  return (
    <AbsoluteFill>
      <Backdrop />
      {beats.map((beat, i) => {
        const next = beats[i + 1]?.at;
        const appear = interpolate(t, [beat.at - 0.1, beat.at + 0.2], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        // The outgoing beat is almost gone before the next one is legible.
        // Overlapping them at the same size in the same place stacks two
        // sentences on top of each other, which reads as a broken render.
        const leave =
          next === undefined
            ? 1
            : interpolate(t, [next - 0.22, next - 0.04], [1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              });
        const opacity = Math.min(appear, leave);
        if (opacity <= 0.002) return null;

        // Leaving lifts away, so the brief crossover reads as movement
        // rather than as two beats sharing the centre of the frame.
        const exit = (1 - leave) * -34;

        return (
          <AbsoluteFill
            key={i}
            style={{
              justifyContent: "center",
              alignItems: "center",
              padding: "0 210px",
              opacity,
              transform: `translateY(${exit}px)`,
            }}
          >
            <div style={{ maxWidth: 1480, textAlign: "center" }}>
              {beat.em ? <Rule progress={appear} /> : null}
              {beat.lines.map((line, k) => (
                <Line
                  key={k}
                  text={line}
                  em={beat.em}
                  size={sizeFor(beat.lines)}
                  // Frames since this line should have started moving.
                  elapsed={(t - beat.at) * fps - k * 3}
                  fps={fps}
                />
              ))}
            </div>
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};

/** Fit the longest line inside the safe width instead of trusting one size. */
function sizeFor(lines: string[]) {
  const longest = Math.max(...lines.map((l) => l.length));
  const fitted = 1440 / (0.47 * Math.max(longest, 1));
  return Math.max(42, Math.min(92, fitted));
}

const Line: React.FC<{
  text: string;
  em?: boolean;
  size: number;
  elapsed: number;
  fps: number;
}> = ({ text, em, size, elapsed, fps }) => {
  const s = spring({
    frame: Math.max(0, elapsed),
    fps,
    config: { damping: 200, stiffness: 92, mass: 0.68 },
  });
  const lift = interpolate(s, [0, 1], [40, 0]);

  return (
    <div
      style={{
        transform: `translateY(${lift}px)`,
        fontFamily: em ? DISPLAY : BODY,
        fontWeight: em ? 700 : 600,
        fontSize: em ? size * 0.88 : size,
        lineHeight: 1.2,
        letterSpacing: em ? 1.5 : 0.4,
        color: em ? BRAND.pink : BRAND.text,
        textShadow: em
          ? `0 0 46px rgba(255,20,147,0.42), 0 4px 20px rgba(0,0,0,0.6)`
          : "0 4px 20px rgba(0,0,0,0.6)",
        padding: "6px 0",
      }}
    >
      {text}
    </div>
  );
};

/** A short pink rule that draws itself above an emphasised beat. */
const Rule: React.FC<{ progress: number }> = ({ progress }) => (
  <div
    style={{
      width: interpolate(progress, [0, 1], [0, 132]),
      height: 5,
      margin: "0 auto 34px",
      background: `linear-gradient(90deg, ${BRAND.pink}, ${BRAND.pinkSoft})`,
    }}
  />
);

/**
 * The type scenes sit between finished stills whose backgrounds glow, so a
 * flat fill would read as a hole in the video. This drifts slowly enough to
 * stay out of the way.
 */
const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const drift = Math.sin((frame / fps) * 0.26);

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.background }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at ${50 + drift * 9}% ${
            44 + drift * 6
          }%, rgba(255,20,147,0.26) 0%, rgba(255,20,147,0.07) 34%, rgba(14,11,31,0) 62%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at ${28 - drift * 7}% 78%, rgba(168,159,203,0.16) 0%, rgba(14,11,31,0) 52%)`,
        }}
      />
    </AbsoluteFill>
  );
};
