import type { ModuleConfig } from "../types";

/**
 * Module 01.
 *
 * `at` is the second the voiceover reaches that slide. These came from
 * listening to the recording; the deck's text tells you nothing about pace,
 * and evenly spacing slides puts every one on the wrong sentence.
 *
 * Scrub the Studio timeline and edit these numbers - the preview reloads as
 * you type, so a slide that lands early or late takes seconds to correct.
 * Slides without `at` divide the gap between their anchored neighbours.
 */
export const module01: ModuleConfig = {
  id: "module-01",
  title: "MODULE 01",
  subtitle: "The Viral Content Formula",
  narration: "module-01/narration.mp3",
  durationInSeconds: 243.9,
  slidesDir: "module-01/slides",
  shotsDir: "module-01/screenshots",
  slides: [
    { image: "slide-01.png" },
    { image: "slide-02.png" },
    { image: "slide-03.png" },
    { image: "slide-04.png" },
    { image: "slide-05.png" },
    {
      image: "slide-06.png",
      at: 33,
      shots: [{ src: "01-content-engine.png", caption: "Open your Content Engine project" }],
    },
    {
      image: "slide-07.png",
      at: 43,
      shots: [{ src: "02-hook-writer.png", caption: "Use the hook-writer skill" }],
    },
    {
      image: "slide-08.png",
      at: 73,
      shots: [{ src: "03-score-hooks.png", caption: "Score and rank the top 5" }],
    },
    { image: "slide-09.png", at: 78 },
    { image: "slide-10.png", at: 88 },
    {
      image: "slide-11.png",
      at: 116,
      shots: [{ src: "04-full-formula.png", caption: "Value point, format, 3 CTAs" }],
    },
    {
      image: "slide-12.png",
      at: 153,
      shots: [{ src: "05-content-calendar.png", caption: "Save it to your calendar row" }],
    },
    { image: "slide-13.png", at: 177 },
    { image: "slide-14.png" },
  ],
};
