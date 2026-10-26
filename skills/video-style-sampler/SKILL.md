---
name: video-style-sampler
description: "Compare video styles side-by-side for owner selection."
version: 1.0.0
author: jarvis
license: proprietary
category: creative
metadata:
  hermes:
    tags: [video, style, comparison, sampler, owner-selection]
    related_skills: [motion-graphics, hyperframes-video-production, product-launch-video]
---

# video-style-sampler: Same Content, N Styles, Side-by-Side

When the owner says two versions "look the same" or asks to "see the styles / post them side by side",
do NOT re-render the same look and do NOT defend it as a style change. Produce a **style sampler**: one
fixed piece of content rendered in N genuinely different art styles, delivered on ONE screen so the
choice is obvious. This class applies to video reels, explainers, shorts and promo films.

## When to Use

- The owner says two video versions "look the same" or asks "what styles do we have" / "post the styles side by side".
- Any situation where a visual direction must be chosen and the owner should see real options, not descriptions.
- Do NOT use for editing an existing clip, converting footage, or building one style -- those belong to the video-editing / motion-graphics skills.

## Step 0: Diagnose version-vs-style BEFORE answering (the trigger)

If v1/v2 were described as different styles but the owner reports they look identical, verify they ARE
different before ever claiming so:

- Diff BRIEF / SCRIPT / STORYBOARD between the two versions (byte-identical => no content change).
- Diff the design tokens in the shared `scene_common.py` / build module that generates all scenes
  (palette, type, motion tokens unchanged => same style).

A v2 is very often an **ENGINE rebuild of the SAME style** -- the picture changes, the art style does not.
Then "they look the same" is CORRECT: say so plainly, then offer the sampler as the real next step.
Never let a version bump masquerade as a style change.

## Step 1: Lock the content (only the style may vary)

- One fixed script with exact spoken lines, identical across every style.
- ONE shared VO generated once (local Kokoro ONNX:
  `env -u PYTHONPATH [REDACTED_PATH]`) and muxed into every clip. Generating audio
  per-style introduces timing drift and length mismatch that makes clips incomparable.
- ONE shared caption word-timing (`faster-whisper base.en word_timestamps=True`); each style draws its
  own caption idiom from the SAME timings.
- Fix total duration and resolution up front (e.g. 12.000 s / 360 frames @ 30fps, 1080x1920 vertical).

## Step 2: Pick genuinely DISTINCT styles; always include the baseline as the CONTROL

- Select styles that differ at a glance (palette + type + motion), e.g. `flight-status` (dark aerospace
  dossier) vs `editorial-collage` (Vox torn-paper on cream) vs `neo-brutal` (yellow brutalist, black
  borders) vs `blueprint` (cyanotype drafting) vs `paper-lantern` (cut-paper lightbox).
- NEVER pick near-variations of the current style -- that recreates the exact "they all look the same"
  failure. The styles must be describable in one sentence each, and a viewer must tell them apart with
  the sound off.
- Always include the current/baseline style as a labelled CONTROL so the real delta reads clearly.
- Read each style's source of truth before drawing it (motion-graphics 5-name menu,
  `[REDACTED_PATH]>/STYLE.md`, `[REDACTED_PATH]>/DESIGN.md` +
  `tokens.css`); do not blend tokens between styles -- distinctness is the whole point.

## Step 3: Self-label every clip

Burn a style badge top-left into EVERY clip, e.g. `STYLE 02 · EDITORIAL COLLAGE`. An unlabelled grid
forces the owner to open each file to know which is which -- the exact pain the sampler removes.

## Step 4: Build progressively, commit per style

Build, render and verify style 01 first, `git add`/`git commit` that working state, THEN repeat for
02..N. One commit per finished style so a long/risky step cannot lose completed work.

## Step 5: Verify each clip BEFORE compositing

Per clip: `ffprobe` duration == target exactly, frame count, fps; `ffmpeg -vf freezedetect=n=-60dB:d=0.5`
=> 0 events; loudness. Inspect actual frames -- a green ffprobe is NOT proof a style reads on screen.

## Step 6: Composite (ORCHESTRATOR-owned, never the worker agent)

The orchestrator owns the side-by-side grid, NOT the build agent. Produce a 3x2 `xstack` grid for 5
styles (6th cell = generated title card) plus a labelled contact sheet of hero frames at t=6.0 s. The
composite script should be pre-staged so it runs the moment per-style renders land (fixed naming
`renders/style-0X-<slug>.mp4`).

Grid: `xstack=inputs=6:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0` with cells scaled to ~640x1138;
use `-movflags +faststart` for Discord and `-t <exact duration>` so no clip runs long; match `-t` to
content duration.

## Step 7: Deliver, then verify the delivery

Post the composite + contact sheet FIRST (that is the answer), then the individual full-res clips as
follow-up messages. Discord multipart: `payload_json` field naming each attachment (curl `-F` returns
50035 Invalid Form Body) and an explicit bot `User-Agent` (Cloudflare 1010 from a datacenter IP).
Split large sets across messages (~10 MB/file, and keep each message's total well under 25 MB).
A 200 without a message id is not proof -- fetch the channel back and confirm each attachment's
filename and byte size before telling the owner it is posted.

## Pitfalls

- **ffmpeg `drawtext` renders a Python `\u2014` escape literally** as `u2014` in the frame. Pass real
  ASCII/UTF-8 text, or a `textfile=`, never a backslash-escape; then re-extract a still and LOOK at it.

- **lemo style `demo/fonts/` dirs ship ONLY `fonts.css` + `OFL.txt`; the actual `.ttf/.woff2` are absent**
  (font files are unvendored). If a build relies on a lemo style's faces (e.g. `ArchitectsDaughter`,
  `B612`, `Allura`), fetch/install them or substitute the nearest local face and RECORD the substitution
  in the build report. `[REDACTED_PATH]` are decorative per-script faces, NOT general
  latin webfonts.
- **The hyperframes CLI is not on PATH.** Either run `npx hyperframes render ...` from the project dir,
  or `export PATH=[REDACTED_PATH]>/node_modules/.bin:$PATH` then
  `hyperframes render scenes/<slug> --output renders/style-0X-<slug>.mp4 --fps 30 -q high`. Composition
  contract per scene dir: `index.html` + `hyperframes.json`
  `{name, entry, width:1080, height:1920, fps:30, duration:12.0}`.
- **Reuse the prior build's pipeline** (`make_audio.py`, `make_captions.py`, `verify.py`, `scene_common.py`)
  as scaffolding instead of reinventing it; but the shared module's tokens are style-specific and MUST NOT
  leak across sampler variants.
- **$0 spend -- Ag2 only.** No OpenRouter / image / video-gen / paid TTS. Everything local: Kokoro ONNX,
  procedural NumPy/SciPy audio, ffmpeg, hyperframes. Vendor everything a composition needs into its own
  dir; no network at render time (free OFL fonts may be fetched once and committed).
- Dispatches to a worker get the owner-mandated header: an explicit JOB / GOAL / SKILLS / MODEL preamble
  prepended to the brief, a worker ceiling (min 2h TIMEOUT), and a working dir named after the project.
