import React from 'react';
import {
  AbsoluteFill,
  Sequence,
  useVideoConfig,
  interpolate,
  Easing,
  Text,
  useCurrentFrame,
  staticFile,
} from 'remotion';

/**
 * AI Content Engine - Module 00 Remotion Composition
 *
 * This composition recreates the Module 00 video using Remotion.
 * It combines intro, main content, image overlays, and outro sequences.
 */

// Color scheme
const COLORS = {
  primary: '#4DD9E8',    // Cyan
  secondary: '#F3EEFF',  // Light purple
  background: '#0E0B1F', // Dark navy
};

// Intro Card Component
export const IntroCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durationFrames = 3 * fps; // 3 seconds

  const opacity = interpolate(frame, [0, 15, durationFrames - 15, durationFrames], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const scale = interpolate(frame, [0, 30], [0.95, 1], {
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background, opacity }}>
      <AbsoluteFill
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          transform: `scale(${scale})`,
        }}
      >
        <Text
          style={{
            fontSize: 96,
            fontWeight: 'bold',
            color: COLORS.primary,
            marginBottom: 30,
            textAlign: 'center',
            fontFamily: 'Arial',
            letterSpacing: 4,
          }}
        >
          AI CONTENT ENGINE
        </Text>
        <Text
          style={{
            fontSize: 56,
            color: COLORS.secondary,
            textAlign: 'center',
            fontFamily: 'Arial',
            maxWidth: 1000,
            lineHeight: 1.4,
          }}
        >
          Module 00: Set Up Your AI Content Studio
        </Text>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Image Overlay Component
interface ImageOverlayProps {
  imageUrl: string;
  stepNumber: number;
}

export const ImageOverlay: React.FC<ImageOverlayProps> = ({ imageUrl, stepNumber }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durationFrames = 2 * fps; // 2 seconds

  const opacity = interpolate(frame, [0, 10, durationFrames - 10, durationFrames], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const slideIn = interpolate(frame, [0, 15], [-100, 0], {
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ opacity }}>
      <img
        src={imageUrl}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
        }}
      />
      {/* Header bar with step number */}
      <AbsoluteFill
        style={{
          top: 0,
          height: 80,
          background: 'rgba(14, 11, 31, 0.95)',
          display: 'flex',
          alignItems: 'center',
          paddingLeft: 30,
          transform: `translateY(${slideIn}px)`,
        }}
      >
        <Text
          style={{
            fontSize: 48,
            fontWeight: 'bold',
            color: COLORS.primary,
            fontFamily: 'Arial',
          }}
        >
          Step {stepNumber}
        </Text>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// CTA Card Component
export const CTACard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durationFrames = 3 * fps; // 3 seconds

  const opacity = interpolate(frame, [0, 15, durationFrames - 15, durationFrames], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const scale = interpolate(frame, [0, 30], [0.9, 1], {
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background, opacity }}>
      <AbsoluteFill
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          transform: `scale(${scale})`,
        }}
      >
        <Text
          style={{
            fontSize: 72,
            fontWeight: 'bold',
            color: COLORS.primary,
            marginBottom: 40,
            textAlign: 'center',
            fontFamily: 'Arial',
            maxWidth: 1000,
            lineHeight: 1.3,
          }}
        >
          Ready to Build Your Content Engine?
        </Text>
        <Text
          style={{
            fontSize: 48,
            color: COLORS.secondary,
            textAlign: 'center',
            fontFamily: 'Arial',
          }}
        >
          Start creating engaging content today
        </Text>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Main Composition
export const ModuleVideo: React.FC<{
  mainVideoUrl?: string;
  imageUrls?: string[];
}> = ({ mainVideoUrl, imageUrls = [] }) => {
  const { fps } = useVideoConfig();

  // Timing
  const introEnd = 3 * fps; // 3 second intro
  const mainDuration = 60 * fps; // Assume 60 second main video (adjust as needed)
  const mainEnd = introEnd + mainDuration;
  let currentTime = mainEnd;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      {/* Intro */}
      <Sequence from={0} durationInFrames={introEnd}>
        <IntroCard />
      </Sequence>

      {/* Main Video */}
      {mainVideoUrl && (
        <Sequence from={introEnd} durationInFrames={mainDuration}>
          <AbsoluteFill>
            <video
              src={mainVideoUrl}
              style={{
                width: '100%',
                height: '100%',
              }}
              muted
            />
          </AbsoluteFill>
        </Sequence>
      )}

      {/* Image Overlays */}
      {imageUrls.map((imageUrl, index) => {
        const fromFrame = currentTime;
        const durationFrames = 2 * fps;
        currentTime += durationFrames;

        return (
          <Sequence
            key={index}
            from={fromFrame}
            durationInFrames={durationFrames}
          >
            <ImageOverlay imageUrl={imageUrl} stepNumber={index + 1} />
          </Sequence>
        );
      })}

      {/* Outro */}
      <Sequence from={currentTime} durationInFrames={3 * fps}>
        <CTACard />
      </Sequence>
    </AbsoluteFill>
  );
};

export default ModuleVideo;

/**
 * INSTALLATION INSTRUCTIONS
 *
 * 1. Create a new Remotion project:
 *    npx create-video
 *    cd create-video
 *
 * 2. Copy this file to src/MyComposition.tsx
 *
 * 3. Update your src/Root.tsx to include:
 *    import { ModuleVideo } from './MyComposition';
 *
 *    <Composition
 *      id="module-00"
 *      component={ModuleVideo}
 *      durationInFrames={/* total frames */}
 *      fps={30}
 *      width={1920}
 *      height={1080}
 *      defaultProps={{
 *        mainVideoUrl: 'path-to-main-video.mp4',
 *        imageUrls: ['image1.png', 'image2.png', 'image3.png', 'image4.png']
 *      }}
 *    />
 *
 * 4. To render:
 *    npm start
 *    (for development with preview)
 *
 *    npm run build
 *    npx remotion render src/index.ts output.mp4
 *    (for production rendering)
 *
 * ADVANTAGES OF REMOTION
 * ✓ React-based - easy to customize and iterate
 * ✓ Component-driven - reusable segments
 * ✓ Precise timing and animation control
 * ✓ Version control friendly
 * ✓ Supports dynamic content
 * ✓ Fast preview and rendering
 * ✓ Can render to various formats
 */
