import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BODY, BRAND } from "../brand";

/**
 * The caption as a tilted post-it. It springs in rather than cutting, which
 * is what makes the card read as placed on the slide rather than pasted over
 * it.
 */
export const StickyNote: React.FC<{ text: string; delay?: number }> = ({
  text,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, mass: 0.6 },
  });
  const lift = interpolate(enter, [0, 1], [24, 0]);
  const tilt = interpolate(enter, [0, 1], [-9, -3.5]);

  return (
    <div
      style={{
        position: "absolute",
        top: -34,
        left: -26,
        transform: `translateY(${lift}px) rotate(${tilt}deg)`,
        opacity: enter,
        background: BRAND.postit,
        color: BRAND.postitInk,
        fontFamily: BODY,
        fontWeight: 700,
        fontSize: 28,
        padding: "16px 30px",
        boxShadow: "0 10px 24px rgba(0,0,0,0.45)",
        whiteSpace: "nowrap",
        zIndex: 2,
      }}
    >
      {text}
      <div
        style={{
          position: "absolute",
          right: 0,
          bottom: 0,
          width: 0,
          height: 0,
          borderLeft: "22px solid transparent",
          borderBottom: `22px solid rgba(0,0,0,0.12)`,
        }}
      />
    </div>
  );
};
