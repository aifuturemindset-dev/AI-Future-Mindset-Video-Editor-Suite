export type Shot = {
  src: string;
  caption: string;
};

export type Slide = {
  image: string;
  /** Second the voiceover reaches this slide. Omit to share the gap evenly. */
  at?: number;
  shots?: Shot[];
};

export type ModuleConfig = {
  id: string;
  title: string;
  subtitle: string;
  narration: string;
  durationInSeconds: number;
  slidesDir: string;
  shotsDir: string;
  slides: Slide[];
};

export type ResolvedSlide = Slide & {
  start: number;
  end: number;
  index: number;
};

/**
 * Turn anchors into spans. Anchored slides keep their exact second; runs of
 * unanchored slides divide the gap to the next anchor, or to the end of the
 * narration for a trailing run.
 */
export const resolveSlides = (config: ModuleConfig): ResolvedSlide[] => {
  const { slides, durationInSeconds } = config;
  const starts: number[] = new Array(slides.length).fill(NaN);

  slides.forEach((slide, i) => {
    if (slide.at !== undefined) starts[i] = slide.at;
  });
  if (Number.isNaN(starts[0])) starts[0] = 0;

  const anchored = starts
    .map((value, i) => ({ value, i }))
    .filter(({ value }) => !Number.isNaN(value))
    .map(({ i }) => i);

  for (let k = 0; k < anchored.length - 1; k++) {
    const a = anchored[k];
    const b = anchored[k + 1];
    const gap = (starts[b] - starts[a]) / (b - a);
    for (let i = a + 1; i < b; i++) starts[i] = starts[a] + gap * (i - a);
  }

  const last = anchored[anchored.length - 1];
  if (last < slides.length - 1) {
    const gap = (durationInSeconds - starts[last]) / (slides.length - last);
    for (let i = last + 1; i < slides.length; i++) {
      starts[i] = starts[last] + gap * (i - last);
    }
  }

  return slides.map((slide, index) => ({
    ...slide,
    index,
    start: starts[index],
    end: index + 1 < slides.length ? starts[index + 1] : durationInSeconds,
  }));
};
