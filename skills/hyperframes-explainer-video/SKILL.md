---
name: hyperframes-explainer-video
description: Use when building HyperFrames explainer videos.
---

# HyperFrames Explainer Video

Turn a topic, article, or script into a narrated faceless explainer MP4 using the `hyperframes` skills (HeyGen HyperFrames, an HTML/CSS-to-video framework) driven through Claude Code.

## Cost rule (user preference — non-negotiable)

Even when the video's SUBJECT is a frontier model (e.g. Claude Opus 5.5), **never author the composition with that expensive model**. Author with a cheap, verified tier and spend only a few cents:

- Verified cheap option on this install: **`anthropic/claude-sonnet-5`** through OpenRouter (~$2 in / $10 out per MTok).
- The frontier model is only the VIDEO'S CONTENT (facts), never the generator.
- Render is local and free (HyperFrames CLI + installed Chromium + ffmpeg).

**Always verify a model id resolves before committing to it** (`claude -p "Reply OK" --model <id> --max-turns 1` inside a script that sources [REDACTED_PATH] and sets the ANTHROPIC_* env). Doc aliases like `-latest[1m]` and `fable-latest` 400 on this build — test, don't trust docs. Retired model lines (e.g. Opus 4.x) answer but are sunset; prefer the current released tier.

## Workflow

1. **Research first** (facts are the agent's job, not the user's). Gather verified facts for the subject via web_search / delegation, then write `assets/SCRIPT.md` mapping each scene to its narration with timestamps.
2. **Grill decisions** before building: destination (16:9 web / 1:1 feed / 9:16 Shorts), length (30-60s sweet spot for an explainer, ~44s is a good single-pass target), angle (concept / listicle / how-to / cost), voiceover source. Present recommendations; ship with the user's picks.
3. **Generate narration** with `text_to_speech` -> `narration.ogg` (edge TTS works headless).
4. **Scaffold** the project: `npx --yes hyperframes@latest init <name>` — needs an EMPTY directory; scaffold into a fresh dir, then copy the narration+SCRIPT in.
5. **Author the composition via Claude Code** (see step 6), OR drive it directly. The scaffolded project has its own `CLAUDE.md` + installed `hyperframes` skills.
6. **Claude Code prompt** (project dir, use `--allowedTools`):
   `claude -p "Read ./CLAUDE.md ... build a 16:9 faceless explainer about <subject> ... run npm run check and fix errors ... do NOT render yet" --model "anthropic/claude-sonnet-5" --max-turns 40 --allowedTools "Read,Edit,Write,Bash"`
   Expected output: single `index.html` root timeline, `class="clip"` + `data-start`/`data-duration` on one timeline, one paused GSAP timeline registered on `window.__timelines`, deterministic only (no Date.now/Math.random/network). A single-timeline build legitimately triggers `nested_structure_needs_subcomposition` warnings — those are expected and can be ignored.
7. **Wire the narration** into the composition — this is missing from a Claude-Code-author pass and MUST be added manually: insert an `<audio>` element as a child of the root composition div with `data-start="0"`, `data-duration="<video len>"`, and **`src=` (NOT `data-src=`)** pointing at `assets/narration.ogg`.
8. **Check**: `npm run check` (or `npx --yes hyperframes@0.8.65 check`). Requires **0 errors**; contrast should be all-pass (WCAG AA). The 9 sub-composition warnings are fine.
9. **Render**: `npm run render` -> MP4 in `renders/`. Confirm the assemble log says `hasAudio:true`.
10. **Verify independently** — never trust `hasAudio:true` alone. Confirm with ffprobe/ffmpeg: an AAC audio stream exists, duration matches, and the file is non-silent (max_volume well above -30 dB). Only then deliver with `MEDIA:<abs path>`.

## Pitfalls

- **`data-src` fails the renderer check** — the audio element uses plain `src`, not `data-src`. Using `data-src` yields `media_missing_src` ("has data-start but no src").
- **Verify the audio, don't assume it** — a render can report `hasAudio:true` while the track is silent or missing. Always run the ffprobe/volumedetect check (scripts/verify_render.sh) before claiming done.
- **Scaffold into an empty dir** — `hyperframes init` refuses a non-empty directory; scaffold fresh then copy media in, rather than init-in-place.
- **npx version drift** — bare `npx hyperframes` sometimes tries to fetch a nonexistent patch version. Pin the CLI: `npx --yes hyperframes@0.8.65` or use the project's own npm scripts.
- **Unzip may be missing** — the renderer's headless-shell extraction needs `unzip`; install it (`apt-get install -y unzip`) to unblock the runtime check.

## Word-synced narration (captions + kinetic supers + code-drawn action cues)

To make a video whose captions, kinetic supers, AND **code-drawn physical actions** land on the **exact spoken word** ("When the voice says, 'He struck,' the blade moves on struck, not near it, on it") — write the words first, TTS the narration locally (Kokoro ONNX `[REDACTED_PATH]` or free Edge TTS; we do **not** have ElevenLabs installed), run `faster-whisper` back on the synthesized audio to emit `words.json` (`[{w, s, e}, ...]`), lock `EDL.json` (`action_cues` bound to exact word seconds), and only THEN generate the composition code ("Plan it once, check it, code it once, check it, then render it once").
- **Code-drawn character & style consistency:** Define recurring characters once as parameterized JS functions (`drawCharacter(ctx, pose)`) with **cartoon-only anatomy** (big head, simple body, circle hands; `≥ 18–25%` canvas height in wide shots; frame around multi-joint leg/hip bends because procedural 2D human limbs render stiff like a wooden doll), cache static procedural textures (paper grain, washes) to an offscreen `<canvas>` once at setup, and include a continuous in-between state morph in every scene so nothing hangs static.
- **30–45s batch stopwatch rule:** Time every 20–30s render batch against a **30–45s wall-clock window** (`~15–25 fps` floor; Binh's `3,708` frames / `123.6s` rendered in `172s` = `21.6 fps`, whereas our `1,152` frames / `48s` blueprint film took `426.5s` = `2.70 fps` / `177.7s` per 20s batch + `56.0s` redundant mux re-encode). If a batch exceeds `45s` (`< 10 fps`), profile the per-frame draw loop (cull inactive scenes by time window, avoid multiple full-screen scratch canvas blits, and mux audio with `-c:v copy`) before running a full render.
- For free presenter footage, source Pexels / Pixabay / Mixkit clips and confirm with vision that the presenter faces camera and the clip is silent (your TTS is the only audio), then narrate over it. Full recipe + the faster-whisper/PyAV kwarg shim pitfall + the verify-both-tracks rule: `references/word-sync-captions.md` and `[REDACTED_PATH]`.

## Support files

- `scripts/verify_render.sh` — ffprobe stream decode + volumedetect so you prove the MP4 has real audio before delivering.
