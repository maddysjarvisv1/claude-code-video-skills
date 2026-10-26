---
name: remotion-video
description: "Use when building or editing video with Remotion (React)."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, remotion, react, animation, javascript]
    category: creative
---

# Remotion — programmatic video in React

Remotion renders React components to video with headless Chrome + ffmpeg — the same stack as
HyperFrames, so the runtime is already here (node at `[REDACTED_PATH]`).

## When to Use

- The edit is **data-driven** (one composition, many variants: names, prices, stat cards).
- You need React's ecosystem: Tailwind, charts, existing components.
- A developer will maintain it. For a one-off delivered reel, `hyperframes` is the faster path.

## Scaffold + render

```bash
npx create-video@latest --blank        # Remotion 4.x, TypeScript + React
npm i @remotion/cli @remotion/transitions @remotion/google-fonts
npx remotion studio                     # live preview
npx remotion render <CompositionId> out/video.mp4 --concurrency=2 --pixel-format=yuv420p
```

Declare the composition in `src/Root.tsx` with explicit **fps, durationInFrames and resolution** —
all animation math is frame-based.

## Animation API (use this, not CSS keyframes)

```tsx
import {useCurrentFrame, useVideoConfig, interpolate, spring, Easing, Sequence} from 'remotion';

const frame = useCurrentFrame();
const {fps} = useVideoConfig();

// entrance: tiny overshoot, then settle (house motion rule)
const s = spring({frame, fps, config: {damping: 14, stiffness: 120, mass: 0.8}});
const scale = interpolate(s, [0, 1], [0.85, 1]);

// timed ramp — ALWAYS clamp
const opacity = interpolate(frame, [0, 12], [0, 1],
  {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

const x = interpolate(frame, [10, 40], [-120, 0],
  {easing: Easing.bezier(0.2, 0.8, 0.2, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

<Sequence from={30} durationInFrames={90}><Card/></Sequence>
```

- `Sequence` for scenes/layers, `Series` for back-to-back scenes.
- `spring` for entrances, `interpolate` for ramps, `Easing.bezier` for custom curves.
- Deterministic: frame N always renders identically.

## Transitions (`@remotion/transitions`)

```tsx
import {TransitionSeries, linearTiming, springTiming} from '@remotion/transitions';
import {slide} from '@remotion/transitions/slide';

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}><ShotA/></TransitionSeries.Sequence>
  <TransitionSeries.Transition presentation={slide({direction: 'from-right'})}
      timing={springTiming({config: {damping: 200}, durationInFrames: 18})}/>
  <TransitionSeries.Sequence durationInFrames={120}><ShotB/></TransitionSeries.Sequence>
</TransitionSeries>
```

Presentations: `fade`, `slide`, `wipe`, `flip`, `clockWipe`, `none`. **A transition CONSUMES
frames** — total = sum of scenes minus overlapping transition durations.

## Audio

`<Audio src={staticFile('music.mp3')} volume={0.35}/>`; `@remotion/media-utils` for waveforms.
Music ≈ −14 LUFS under the voice; three separate stems (voice/music/sfx), never bake SFX into music —
same rule as `autonomous-video-editor`.

## Pitfalls

- **`--concurrency=2` on a small VPS** — the default can OOM headless Chrome mid-render.
- `--pixel-format=yuv420p` is required or some players show nothing.
- Assets go in `public/` via `staticFile()`, never a raw path.
- **A render not awaited on the same turn produces nothing** — foreground-render and wait for the file
  (the exact failure that made a Sonnet video run return empty).
- Remotion is **licensed** — free for individuals/small companies, paid for larger orgs; check before
  shipping client work.
- fps is fixed at composition time; a 30 fps composition is not interchangeable with 60 fps.
