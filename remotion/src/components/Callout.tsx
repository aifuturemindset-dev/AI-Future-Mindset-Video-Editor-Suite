import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BODY, BRAND } from "../brand";

export type Box = { x: number; y: number; width: number; height: number };

/**
 * Where the label sits relative to the target. The arrow always curves from
 * the label to the nearest edge of the box.
 */
export type LabelSide = "left" | "right" | "above" | "below";

const LABEL_GAP = 150;

const labelAnchor = (box: Box, side: LabelSide) => {
  const cx = box.x + box.width / 2;
  const cy = box.y + box.height / 2;
  switch (side) {
    case "left":
      return { lx: box.x - LABEL_GAP, ly: cy, tx: box.x, ty: cy };
    case "right":
      return { lx: box.x + box.width + LABEL_GAP, ly: cy, tx: box.x + box.width, ty: cy };
    case "above":
      return { lx: cx, ly: box.y - LABEL_GAP, tx: cx, ty: box.y };
    default:
      return { lx: cx, ly: box.y + box.height + LABEL_GAP, tx: cx, ty: box.y + box.height };
  }
};

/**
 * Points at a spot in the frame the way the tutorial screenshots do: a box
 * around the control, a curved arrow, and a label naming the action.
 *
 * Use it over raw screen footage, where there is nothing to point at
 * otherwise. Coordinates are in composition space (1920x1080 by default), so
 * read them straight off a still of the frame you are annotating.
 */
export const Callout: React.FC<{
  box: Box;
  label: string;
  side?: LabelSide;
  delay?: number;
  /** Frame at which the callout fades out. Omit to hold to the end. */
  outAt?: number;
}> = ({ box, label, side = "left", delay = 0, outAt }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const local = frame - delay;

  const enter = spring({ frame: local, fps, config: { damping: 15, mass: 0.7 } });
  const leave = outAt === undefined
    ? 1
    : interpolate(frame, [outAt - 10, outAt], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const opacity = Math.min(enter, leave);

  // A slow pulse keeps the eye on the target through a long hold without
  // the box ever leaving the control it marks.
  const pulse = local < 0 ? 0 : (Math.sin(local / 9) + 1) / 2;
  const glow = interpolate(pulse, [0, 1], [8, 22]);

  const { lx, ly, tx, ty } = labelAnchor(box, side);

  // Bow the arrow perpendicular to its run so it reads as drawn by hand.
  const mx = (lx + tx) / 2;
  const my = (ly + ty) / 2;
  const horizontal = side === "left" || side === "right";
  const bow = horizontal ? -46 : 46;
  const path = `M ${lx} ${ly} Q ${mx + (horizontal ? 0 : bow)} ${my + (horizontal ? bow : 0)} ${tx} ${ty}`;

  const draw = interpolate(enter, [0, 1], [1, 0]);

  return (
    <div style={{ position: "absolute", inset: 0, opacity, pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: box.x,
          top: box.y,
          width: box.width,
          height: box.height,
          border: `4px solid ${BRAND.pink}`,
          borderRadius: 6,
          boxShadow: `0 0 ${glow}px ${BRAND.pink}`,
          transform: `scale(${interpolate(enter, [0, 1], [1.25, 1])})`,
        }}
      />

      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <marker
            id="calloutHead"
            markerWidth="9"
            markerHeight="9"
            refX="7"
            refY="4.5"
            orient="auto"
          >
            <path d="M0,0 L9,4.5 L0,9 z" fill={BRAND.pink} />
          </marker>
        </defs>
        <path
          d={path}
          stroke={BRAND.pink}
          strokeWidth={7}
          strokeLinecap="round"
          fill="none"
          markerEnd="url(#calloutHead)"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={draw}
        />
      </svg>

      <div
        style={{
          position: "absolute",
          left: lx,
          top: ly,
          transform: `translate(${side === "left" ? "-100%" : side === "right" ? "0" : "-50%"}, -50%)`,
          background: "#FFFFFF",
          color: "#12101F",
          fontFamily: BODY,
          fontWeight: 700,
          fontSize: 30,
          padding: "10px 22px",
          borderRadius: 8,
          boxShadow: "0 8px 22px rgba(0,0,0,0.45)",
          whiteSpace: "nowrap",
        }}
      >
        {label}
      </div>
    </div>
  );
};
