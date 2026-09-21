import type { AnnotatedVideoConfig } from "../AnnotatedVideo";

/**
 * Demonstrates callouts over raw footage.
 *
 * Box coordinates are read off a still of the frame being annotated:
 *   ffmpeg -ss 4 -i public/demo/raw-clip.mp4 -frames:v 1 /tmp/frame.png
 * The composition is 1920x1080, so pixel positions in that still are the
 * numbers below.
 */
export const demoAnnotated: AnnotatedVideoConfig = {
  id: "demo-annotated",
  video: "demo/raw-clip.mp4",
  durationInSeconds: 10,
  annotations: [
    {
      at: 1,
      until: 5,
      box: { x: 1180, y: 300, width: 420, height: 90 },
      label: "Click New project",
      side: "left",
      skill: "hook-writer",
    },
    {
      at: 5.5,
      until: 9.5,
      box: { x: 300, y: 620, width: 520, height: 110 },
      label: "Paste your brand voice",
      side: "above",
      skill: "brand-voice",
    },
  ],
};
