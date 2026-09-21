import { staticFile } from "remotion";

/**
 * Tokens lifted from the course kit's own stylesheet (course-hub.html and
 * slide-decks.html), dark theme. Change them here and every composition
 * follows.
 */
export const BRAND = {
  pink: "#FF1493",
  pinkSoft: "#FF7AC6",
  text: "#F3EEFF",
  muted: "#A89FCB",
  background: "#0E0B1F",
  panel: "#171331",
  line: "#2E2754",
  postit: "#FFE86B",
  postitInk: "#2A2416",
  wordmark: "AI FUTURE MINDSET",
  title: "AI CONTENT ENGINE",
} as const;

export const DISPLAY = "Orbitron";
export const BODY = "Rajdhani";

/**
 * Fonts are served from public/ rather than a CDN: Google Fonts and jsdelivr
 * are both blocked in the build environment, and a local file also keeps
 * renders deterministic.
 */
export const fontFaces = `
@font-face {
  font-family: '${DISPLAY}';
  src: url('${staticFile("fonts/Orbitron-Bold.ttf")}') format('truetype');
  font-weight: 700;
}
@font-face {
  font-family: '${DISPLAY}';
  src: url('${staticFile("fonts/Orbitron-Regular.ttf")}') format('truetype');
  font-weight: 400;
}
@font-face {
  font-family: '${BODY}';
  src: url('${staticFile("fonts/Rajdhani-Bold.ttf")}') format('truetype');
  font-weight: 700;
}
@font-face {
  font-family: '${BODY}';
  src: url('${staticFile("fonts/Rajdhani-SemiBold.ttf")}') format('truetype');
  font-weight: 600;
}
@font-face {
  font-family: '${BODY}';
  src: url('${staticFile("fonts/Rajdhani-Regular.ttf")}') format('truetype');
  font-weight: 400;
}
`;
