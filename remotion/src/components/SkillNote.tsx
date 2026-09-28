import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BODY, BRAND, DISPLAY } from "../brand";

type Corner = "top-left" | "top-right" | "bottom-left" | "bottom-right";

const place = (corner: Corner) => {
  const inset = 56;
  return {
    top: corner.startsWith("top") ? inset : undefined,
    bottom: corner.startsWith("bottom") ? inset : undefined,
    left: corner.endsWith("left") ? inset : undefined,
    right: corner.endsWith("right") ? inset : undefined,
  };
};

/**
 * A post-it naming the skill in use, pinned to a corner.
 *
 * Worth keeping on screen for the whole step rather than flashing it: a
 * viewer who joins mid-step still needs to know which skill produced what
 * they are looking at.
 */
export const SkillNote: React.FC<{
  skill: string;
  eyebrow?: string;
  corner?: Corner;
  delay?: number;
  outAt?: number;
}> = ({ skill, eyebrow = "SKILL", corner = "top-right", delay = 0, outAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - delay;

  const enter = spring({ frame: local, fps, config: { damping: 13, mass: 0.6 } });
  const leave = outAt === undefined
    ? 1
    : interpolate(frame, [outAt - 10, outAt], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

  const tilt = interpolate(enter, [0, 1], [-11, -3]);
  const drop = interpolate(enter, [0, 1], [-30, 0]);

  return (
    <div
      style={{
        position: "absolute",
        ...place(corner),
        transform: `translateY(${drop}px) rotate(${tilt}deg)`,
        opacity: Math.min(enter, leave),
        background: BRAND.postit,
        color: BRAND.postitInk,
        padding: "18px 28px 20px",
        boxShadow: "0 14px 30px rgba(0,0,0,0.5)",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          fontFamily: DISPLAY,
          fontWeight: 700,
          fontSize: 14,
          letterSpacing: 5,
          opacity: 0.66,
          marginBottom: 4,
        }}
      >
        {eyebrow}
      </div>
      <div style={{ fontFamily: BODY, fontWeight: 700, fontSize: 34, whiteSpace: "nowrap" }}>
        {skill}
      </div>
    </div>
  );
};
