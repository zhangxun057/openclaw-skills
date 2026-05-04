---
name: remotion-best-practices
description: |
  Remotion best practices - React-based video framework domain knowledge.
  Use whenever dealing with Remotion code to obtain domain-specific knowledge.
author: remotion-dev
source: https://github.com/remotion-dev/skills
version: 1.0.0
---

## When to use

Use this skills whenever you are dealing with Remotion code to obtain the domain-specific knowledge.

## New project setup

When in an empty folder or workspace with no existing Remotion project, scaffold one using:

npx create-video@latest --yes --blank --no-tailwind my-video

Replace my-video with a suitable project name.

## Designing a video

Animate properties using useCurrentFrame() and interpolate(). Use Easing to customize the timing of the animation.

```tsx
import { useCurrentFrame, Easing } from "remotion";

export const FadeIn = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 2 * fps], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return <div style={{ opacity }}>Hello World!</div>;
};
```

CSS transitions or animations are FORBIDDEN - they will not render correctly.

Tailwind animation class names are FORBIDDEN - they will not render correctly.

Place assets in the public/ folder at your project root.

Use staticFile() to reference files from the public/ folder.

Add images using the `<Img>` component:

```tsx
import { Img, staticFile } from "remotion";

export const MyComposition = () => {
  return <Img src={staticFile("logo.png")} style={{ width: 100, height: 100 }} />;
};
```

Add videos using the `<Video>` component from @remotion/media:

```tsx
import { Video } from "@remotion/media";
import { staticFile } from "remotion";

export const MyComposition = () => {
  return <Video src={staticFile("video.mp4")} style={{ opacity: 0.5 }} />;
};
```

Add audio using the `<Audio>` component from @remotion/media:

```tsx
import { Audio } from "@remotion/media";
import { staticFile } from "remotion";

export const MyComposition = () => {
  return <Audio src={staticFile("audio.mp3")} />;
};
```

Assets can be also referenced as remote URLs:

```tsx
import { Video } from "@remotion/media";

export const MyComposition = () => {
  return <Video src="https://remotion.media/video.mp4" />
};
```

To delay content wrap it in `<Sequence>` and use from.
To limit the duration of an element, use durationInFrames of `<Sequence>`.
`<Sequence>` by default is an absolute fill. For inline content, use `layout="none"`.

```tsx
import { Sequence } from "remotion";

export const Title = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 2 * fps], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return <div style={{ opacity }}>Title</div>;
};

export const Subtitle = () => {
  return <div>Subtitle</div>;
};

const Main = () => {
  const {fps} = useVideoConfig();

  return (
    <AbsoluteFill>
      <Sequence>
        <Background />
      </Sequence>
      <Sequence from={1 * fps} durationInFrames={2 * fps} layout="none">
        <Title />
      </Sequence>
      <Sequence from={2 * fps} durationInFrames={2 * fps} layout="none">
        <Subtitle />
      </Sequence>
    </AbsoluteFill>
  );
}
```

The width, height, fps, and duration of a video is defined in src/Root.tsx:

```tsx
import { Composition } from "remotion";
import { MyComposition } from "./MyComposition";

export const RemotionRoot = () => {
  return (
    <Composition
      id="MyComposition"
      component={MyComposition}
      durationInFrames={100}
      fps={30}
      width={1080}
      height={1080}
    />
  );
};
```

Metadata can also be calculated dynamically:

```tsx
import { Composition, CalculateMetadataFunction } from "remotion";
import { MyComposition, MyCompositionProps } from "./MyComposition";

const calculateMetadata: CalculateMetadataFunction<
  MyCompositionProps
> = async ({ props, abortSignal }) => {
  const data = await fetch(`https://api.example.com/video/${props.videoId}`, {
    signal: abortSignal,
  }).then((res) => res.json());

  return {
    durationInFrames: Math.ceil(data.duration * 30),
    props: {
      ...props,
      videoUrl: data.url,
    },
    width: 1080,
    height: 1080,
  };
};

export const RemotionRoot = () => {
  return (
    <Composition
      id="MyComposition"
      component={MyComposition}
      fps={30}
      width={1080}
      height={1080}
      defaultProps={{ videoId: "abc123" }}
      calculateMetadata={calculateMetadata}
    />
  );
};
```

## Starting preview

Start the Remotion Studio to preview a video:

```
npx remotion studio
```

## Optional: one-frame render check

You can render a single frame with the CLI to sanity-check layout, colors, or timing.

Skip it for trivial edits, pure refactors, or when you already have enough confidence from Studio or prior renders.

```
npx remotion still [composition-id] --scale=0.25 --frame=30
```

At 30 fps, `--frame=30` is the one-second mark (`--frame` is zero-based).

## Captions

When dealing with captions or subtitles, load the subtitles rules from the remotion skill repository.

## Using FFmpeg

For some video operations, such as trimming videos or detecting silence, FFmpeg should be used.

## Silence detection

When needing to detect and trim silent segments from video or audio files, use silence detection rules.

## Audio visualization

When needing to visualize audio (spectrum bars, waveforms, bass-reactive effects), use audio visualization rules.

## Sound effects

When needing to use sound effects, use SFX rules.

## 3D content

For 3D content in Remotion using Three.js and React Three Fiber.

## Advanced audio

For advanced audio features like trimming, volume, speed, pitch.

## Dynamic duration, dimensions and data

For dynamically set composition duration, dimensions, and props.

## Advanced compositions

For how to define stills, folders, default props and for how to nest compositions.

## Google Fonts

Is the recommended way to load fonts in Remotion.

## Local fonts

For how to load local fonts.

## Getting audio duration

For getting the duration of an audio file in seconds with Mediabunny.

## Getting video dimensions

For getting the width and height of a video file with Mediabunny.

## Getting video duration

For getting the duration of a video file in seconds with Mediabunny.

## GIFs

For how to display GIFs synchronized with Remotion's timeline.

## Advanced Images

For sizing and positioning images, dynamic image paths, and getting image dimensions.

## Light leaks

For light leak overlay effects using @remotion/light-leaks.

## Lottie animations

For embedding Lottie animations in Remotion.

## Measuring DOM nodes

For measuring DOM element dimensions in Remotion.

## Measuring text

For measuring text dimensions, fitting text to containers, and checking overflow.

## Advanced sequencing

For more sequencing patterns - delay, trim, limit duration of items.

## TailwindCSS

For using TailwindCSS in Remotion.

## Text animations

For typography and text animation patterns.

## Advanced timing

For advanced timing with interpolate and Bézier easing, and springs.

## Transitions

For scene transition patterns.

## Transparent videos

For rendering out a video with transparency.

## Trimming

For trimming patterns - cutting the beginning or end of animations.

## Advanced Videos

For advanced knowledge about embedding videos - trimming, volume, speed, looping, pitch.

## Parameterized videos

For making a composition parametrizable by adding a Zod schema.

## Maps

For adding a map using Mapbox and animating it.

## Voiceover

For adding AI-generated voiceover to Remotion compositions using ElevenLabs TTS.
