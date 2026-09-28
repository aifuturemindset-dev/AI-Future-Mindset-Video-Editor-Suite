import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, staticFile, useVideoConfig } from "remotion";
import { BRAND, fontFaces } from "./brand";
import { Callout, type Box, type LabelSide } from "./components/Callout";
import { SkillNote } from "./components/SkillNote";

export type Annotation = {
  /** Seconds into the clip where the callout appears. */
  at: number;
  /** Seconds where it disappears. */
  until: number;
  box: Box;
  label: string;
  side?: LabelSide;
  /** Names the skill in use; drawn as a post-it for the same span. */
  skill?: string;
};

export type AnnotatedVideoConfig = {
  id: string;
  video: string;
  durationInSeconds: number;
  annotations: Annotation[];
};

/**
 * Raw screen footage with click targets marked.
 *
 * Screen recordings show a cursor moving but not where attention belongs, so
 * a viewer following along misses the control being clicked. Boxing the
 * target and naming the action is what the tutorial screenshots do; this
 * applies the same treatment to moving footage.
 *
 * Read box coordinates off a still of the frame:
 *   ffmpeg -ss 4 -i clip.mp4 -frames:v 1 frame.png
 * The composition is 1920x1080, so pixel positions in that still are the
 * numbers to use.
 */
export const AnnotatedVideo: React.FC<{ config: AnnotatedVideoConfig }> = ({ config }) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.background }}>
      <style>{fontFaces}</style>
      <OffthreadVideo src={staticFile(config.video)} />

      {config.annotations.map((note, i) => {
        const from = Math.round(note.at * fps);
        const duration = Math.max(1, Math.round((note.until - note.at) * fps));
        return (
          <Sequence key={i} from={from} durationInFrames={duration} layout="none">
            <Callout
              box={note.box}
              label={note.label}
              side={note.side}
              outAt={duration - 2}
            />
            {note.skill ? (
              <SkillNote skill={note.skill} delay={6} outAt={duration - 2} />
            ) : null}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
