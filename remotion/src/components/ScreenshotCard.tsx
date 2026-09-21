import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BODY, BRAND } from "../brand";
import { StickyNote } from "./StickyNote";

/**
 * A framed screenshot that slides in from the right and settles. The frame
 * is brand pink, which matches the magenta callout arrows already drawn on
 * the screenshots themselves.
 */
export const ScreenshotCard: React.FC<{
  src: string;
  caption: string;
  position?: number;
  total?: number;
  outAt?: number;
}> = ({ src, caption, position = 1, total = 1, outAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame, fps, config: { damping: 16, mass: 0.8 } });
  const slide = interpolate(enter, [0, 1], [90, 0]);

  const leave = outAt === undefined
    ? 1
    : interpolate(frame, [outAt - 10, outAt], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

  return (
    <div
      style={{
        position: "absolute",
        right: 60,
        top: 420,
        transform: `translateX(${slide}px)`,
        opacity: Math.min(enter, leave),
      }}
    >
      <div
        style={{
          position: "relative",
          background: BRAND.panel,
          border: `3px solid ${BRAND.pink}`,
          borderRadius: 16,
          padding: 20,
          boxShadow: "0 18px 40px rgba(0,0,0,0.55)",
        }}
      >
        <StickyNote text={caption} delay={4} />
        {total > 1 ? (
          <div
            style={{
              fontFamily: BODY,
              fontWeight: 700,
              fontSize: 22,
              color: BRAND.pink,
              letterSpacing: 1,
              marginBottom: 10,
            }}
          >
            STEP {position} OF {total}
          </div>
        ) : null}
        <Img
          src={staticFile(src)}
          style={{
            display: "block",
            width: 560,
            border: `4px solid ${BRAND.pink}`,
            borderRadius: 4,
          }}
        />
      </div>
    </div>
  );
};
