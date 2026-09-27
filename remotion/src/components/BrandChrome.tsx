import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { BODY, BRAND, DISPLAY } from "../brand";

/**
 * The frame that sits over every scene: corner brackets, the wordmark, and a
 * progress rule along the bottom.
 *
 * It stays off the middle of the frame on purpose. The storyboard stills are
 * finished designs with their own margins, and anything drawn into that area
 * competes with type that is already there.
 */
export const BrandChrome: React.FC<{
  /** Slightly heavier over the stills, which are busier than the type scenes. */
  strength?: number;
}> = ({ strength = 1 }) => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();

  const inset = 40;
  const arm = 120;
  const weight = 5;
  const corners = [
    { left: inset, top: inset, sx: 1, sy: 1 },
    { left: width - inset, top: inset, sx: -1, sy: 1 },
    { left: inset, top: height - inset, sx: 1, sy: -1 },
    { left: width - inset, top: height - inset, sx: -1, sy: -1 },
  ];

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {corners.map((c, i) => (
        <React.Fragment key={i}>
          <div
            style={{
              position: "absolute",
              left: c.sx > 0 ? c.left : c.left - arm,
              top: c.top - weight / 2,
              width: arm,
              height: weight,
              backgroundColor: BRAND.pink,
              opacity: 0.85 * strength,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: c.left - weight / 2,
              top: c.sy > 0 ? c.top : c.top - arm,
              width: weight,
              height: arm,
              backgroundColor: BRAND.pink,
              opacity: 0.85 * strength,
            }}
          />
        </React.Fragment>
      ))}

      <div
        style={{
          position: "absolute",
          left: inset + 30,
          bottom: inset + 26,
          fontFamily: DISPLAY,
          fontWeight: 700,
          fontSize: 22,
          letterSpacing: 9,
          color: BRAND.pink,
          textShadow: "0 2px 14px rgba(0,0,0,0.85)",
        }}
      >
        {BRAND.wordmark}
      </div>

      <div
        style={{
          position: "absolute",
          right: inset + 30,
          bottom: inset + 26,
          fontFamily: BODY,
          fontWeight: 600,
          fontSize: 21,
          letterSpacing: 3,
          color: BRAND.muted,
          textShadow: "0 2px 14px rgba(0,0,0,0.85)",
        }}
      >
        THE 100-DAY AI FINISH LINE
      </div>

      {/* Progress along the very bottom edge, so a viewer can feel the shape
          of the video without a scrub bar. */}
      <div
        style={{
          position: "absolute",
          left: 0,
          bottom: 0,
          height: 6,
          width: `${(frame / durationInFrames) * 100}%`,
          background: `linear-gradient(90deg, ${BRAND.pink}, ${BRAND.pinkSoft})`,
        }}
      />
    </AbsoluteFill>
  );
};
