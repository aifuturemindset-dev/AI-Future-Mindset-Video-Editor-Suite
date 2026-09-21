import React from "react";
import { AbsoluteFill } from "remotion";
import { BODY, BRAND, DISPLAY } from "../brand";

/**
 * Brand frame drawn over a slide: wordmark, slide counter, base rule and a
 * progress bar. Kept thin deliberately - the deck carries its own design and
 * a second heavy layer buries it.
 */
export const Chrome: React.FC<{
  index: number;
  total: number;
  progress: number;
  showWordmark?: boolean;
}> = ({ index, total, progress, showWordmark = true }) => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    {showWordmark ? (
      <div
        style={{
          position: "absolute",
          top: 26,
          left: 36,
          fontFamily: DISPLAY,
          fontWeight: 700,
          fontSize: 18,
          letterSpacing: 8,
          color: BRAND.pink,
        }}
      >
        {BRAND.wordmark}
      </div>
    ) : null}

    <div
      style={{
        position: "absolute",
        top: 24,
        right: 40,
        fontFamily: BODY,
        fontWeight: 700,
        fontSize: 26,
        color: BRAND.pink,
        background: "rgba(14,11,31,0.78)",
        padding: "4px 14px",
        borderRadius: 6,
      }}
    >
      {index + 1} / {total}
    </div>

    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 5, background: BRAND.line }}>
      <div
        style={{
          width: `${Math.max(0, Math.min(1, progress)) * 100}%`,
          height: "100%",
          background: BRAND.pink,
        }}
      />
    </div>
  </AbsoluteFill>
);
