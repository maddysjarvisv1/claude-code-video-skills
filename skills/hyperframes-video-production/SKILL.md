---
name: hyperframes-video-production
description: Build narrated HyperFrames videos to MP4, verified.
---

# HyperFrames Video Production

Turn research, a report, or a topic into a **narrated 16:9 explainer MP4** via HeyGen HyperFrames (HTML -> MP4) the cost-conscious way this user wants.

## When to Use
- User wants an "explainer video" / "turn X into a video" / weekly research rendered to a renderable report asset.
- User asks for a reusable HTML content asset that can later be re-rendered or recut (16:9 + 9:16 from the SAME html is the goal).

## Golden rules (this user, non-negotiable)
1. **NEVER generate the video content with Opus 5.5** — the user has said this repeatedly. Use `anthropic/claude-sonnet-5` ($2/$10, the default mid-tier, replaces Sonnet 4.6) or a DeepSeek Flash tier for authoring. Opus 5.5 is review/planning-only.
2. **A single HyperFrames `index.html` composition is the reusable asset.** The user wants reports saved as HTML they can later render to video (YouTube 16:9 / Shorts 9:16) and reuse across sources. Build responsive scenes, not fixed-16:9 absolute positioning for core content.
3. **Verify before claiming done** — confirm video+audio streams exist and audio is non-silent (see Verification). A successful `npm run render` is NOT the deliverable; an inspectable MP4 is.

## Procedure (One-Line Brief → Level 3 Word-Locked Film)
1. **Expand Level 1 → Level 2 (Research + Style Lock)**: If the user gives a one-line prompt ("Level 1"), consult `<home>/SKILLS.md` to pick a concrete style spec (`<home>/lemo-skillsrc/styles/<slug>/STYLE.md` or `<home>/herk-edit-kit/MOTION_PHILOSOPHY.md`), verify every factual claim via search/repo sources, and write `TREATMENT.md` + `SCRIPT.md`.
2. **Generate the narration audio FIRST** via local **Kokoro ONNX** (`env -u PYTHONPATH <home>/lemo-opuscar/.venv/bin/python`, e.g. `bm_george`/`af_heart`) or free Edge `text_to_speech`. Save to `assets/narration.ogg` (or `assets/master_audio.wav`). *(Honest capability note: we do **not** have ElevenLabs voices or music/SFX installed; use local Kokoro/Edge TTS + procedural Python `sfx.py`/`make_audio.py` normalized to `-14.0 LUFS`.)*
3. **Listen back for exact word seconds (Level 2 → Level 3 Lock)**: Run local `faster-whisper` (`~/.hermes/cache/opt/whisper-venv`, `base.en` with PyAV `metadata_errors` shim) over the generated TTS audio to emit `words.json` (`[{w, s, e}, ...]`), and write `EDL.json` binding every scene's physical visual action (`action_cues`) to its exact spoken-word second **before** writing any HTML/JS. *Why:* "When the voice says, 'He struck,' the blade moves on struck, not near it, on it" — without the TTS → Whisper loopback, the code only knows sentence durations and guesses intra-scene timing.
4. **Scaffold**: `npx --yes hyperframes@latest init <project>` — MUST be an empty/nonexistent dir; it refuses init into a dir that already has files. If you wrote `SCRIPT.md`/`EDL.json`/narration first, init into a fresh dir then copy them in.
5. **Author the composition to those word seconds ("Plan it once, check it, code it once, check it, then render it once")** by driving Claude Code inside the project dir (or via `build/build_comp.py`):
   - `claude -p "<build brief>" --model anthropic/claude-sonnet-5 --max-turns N --allowedTools Read,Edit,Write,Bash` (OpenRouter env must be sourced from <home>/.bashrc; set ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_API_KEY='').
   - Give the brief: aspect (16:9 or 9:16), chosen `STYLE.md`, locked `EDL.json` + `words.json` action cues, single paused root timeline on `window.__timelines`, offscreen `<canvas>` caching for static paper/noise textures, continuous in-between state morphs so nothing hangs static, and (if characters appear) reusable parameterized functions with **cartoon-only anatomy** (big head, simple body, circle hands, `≥ 18–25%` canvas height in wide shots; never realistic multi-joint limbs). Ask it to run `npm run check` + lint and fix, but NOT render yet.
   - VERIFY the model flag actually used Sonnet 5, not Opus — grep the authoring script's `--model` flag afterward and confirm zero Opus references in the project (only the video's SUBJECT text should mention Opus).
6. **Wire the audio track into the composition** (this is the common failure): add inside the root timeline div:
   ```html
   <audio id="narration" class="clip" data-audio-group="voiceover" data-start="0" data-duration="44" src="assets/narration.ogg" preload="auto"></audio>
   ```
   - **PITFALL: the attribute is `src`, NOT `data-src`.** `data-src` passes human review but the linter errors: `media_missing_src: <audio> has data-start but no src`. The renderer cannot load the media.
   - Duration attribute must cover the whole composition (match root `data-duration`).
7. **Check**: `npm run check` — fix all errors. `nested_structure_needs_subcomposition` warnings are EXPECTED/deliberate for a single-timeline explainer (Claude Code chose this; acceptable, they are warnings not errors). Target: 0 errors, contrast AA passing.
8. **Render with the 30–45s Batch Stopwatch Rule**: `npm run render` -> writes `renders/<proj>_<timestamp>.mp4`. Time every 20–30s batch against a **30–45s stopwatch window** (`~15–25 fps` floor; Binh's `3,708` frames / `123.6s` rendered in `172s` = `21.6 fps`, whereas our `1,152` frames / `48s` blueprint film took `426.5s` = `2.70 fps` / `177.7s` per 20s batch + `56.0s` redundant mux re-encode). If a 20–30s batch exceeds `45s` (`< 10 fps`), profile the per-frame draw loop (cache static procedural noise to one offscreen `<canvas>`, draw active strokes directly on `mainCtx` instead of blitting 4 full-screen scratch canvases per frame, cull inactive scenes by time window, and mux audio with `-c:v copy`).
9. **Verify the artifact independently** (ffprobe/ffmpeg, never trust the render's own claim):
   - `ffprobe -v error -show_entries stream=codec_type,codec_name -of ...` — expect a video stream (h264) AND an audio stream (aac), both matching root duration.
   - `ffmpeg -i <mp4> -vf "blackdetect=d=0.04:pix_th=0.10" -an -f null -` — expect `0` black frames.
   - `ffmpeg -i <mp4> -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"` — non-silent = mean_volume in the -3 to -25 dB range (`-14 LUFS` target); max_volume near 0.
   - Extract and inspect a tiled contact sheet (`sheet.jpg`) with vision before delivery.
10. **Deliver**: send `MEDIA:/abs/path/to/output.mp4` (Telegram renders video inline). Offer the project dir for tweaks. Full SOP: `<jarvis-repo>/brain/sops/one-line-film-workflow.md`.

## Pitfalls
- Generating high visual quality per scene is expensive and re-render churn is the real cost — lock `words.json` + `EDL.json` (Level 3) and get `check` + snapshots right before committing to the full encode ("Plan it once, check it, code it once, check it, then render it once").
- A 44s 1920x1080 render took ~1m34s / 1320 frames (~14 fps); our 48s 1080x1920 blueprint film (`1,152` frames @ 24fps) took `426.5s` (`2.70 fps`) + `56.0s` mux because all 8 scenes and 4 full-screen canvases were redrawn every frame and muxed without `-c:v copy`. Commit all source files (`EDL.json`, `words.json`, `index.html`, `build/build.sh`) before starting the render so a timeout never loses work.
- The user wants a lean reusable deck shell + chained writing skills (fragments->shape->beats->humanizer on Sonnet 5) for quality; offer but do not impose.

## Verification (the deliverable standard)
Report: duration, resolution, frame count + render stopwatch speed (`fps`), video+audio streams present, `0` black frames, audio not-silent (mean dB / LUFS), contact sheet inspected, and that the source project dir is saved. Only then is it "done".
