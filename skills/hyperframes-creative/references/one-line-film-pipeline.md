# One-Line Brief → Finished Code-Drawn Film Pipeline

Procedural reference for turning a **single sentence of direction** (Level 1) into a verified, word-locked code-drawn HyperFrames film (Level 3) using only local $0 tools.

Distilled from:
- Binh ("Dad of 3 Monkeys"), *"Claude + Javascript = AMAZING 2D Cartoon Videos At Scale - My Workflow"* (HyperFrames + Claude + JS canvas/DOM, 3,708 frames / 123.6s rendered in 172s, $0 picture spend).
- Our proven local builds: `<home>/hampi-malligi-blueprint` (`48s / 1,152 frames @ 24fps`, blueprint style; measured `426.5s` capture/encode at `2.70 fps` + `56.0s` redundant mux re-encode) and `<home>/malligi-reel` (`30s / 901 frames @ 30fps`, Whisper word-synced, `257s` at `3.51 fps`).

---

## 1. The Three Levels of Asking (Never Code From Level 1 or 2)

- **Level 1 (One sentence)**: *"Make me a cartoon about Zeus."* Unsteerable surprise every time.
- **Level 2 (Style + Brief + Tool)**: *"Show it a style you like, give it a proper brief, hand it HyperFrames."* Aims at the right look, **but the code still guesses the timing** if scenes are only timed to coarse sentence/scene windows.
- **Level 3 (Script + Moment Plan + Exact Word Seconds before Drawing)**: *"Hand over the whole film before it draws a single line: the script, the plan for every moment, and the exact second each word is spoken. When the voice says, 'He struck,' the blade moves on struck, not near it, on it."*
- **House rule**: **"Plan it once, check it, code it once, check it, then render it once."**

When the user supplies a **Level 1** one-line brief, **never jump from Level 1 or Level 2 straight to HTML/JS authoring**. Always construct the **Level 3 package** (`SCRIPT.md` → synthesized voiceover → Whisper `words.json` → word-locked `EDL.json`) first.

---

## 2. Local Capability Matrix (What We Have vs What We Lack)

- **Voiceover**: We do **not** have ElevenLabs installed or configured. Use local **Kokoro ONNX** (`env -u PYTHONPATH <home>/lemo-opuscar/.venv/bin/python`, voices `bm_george`, `af_heart`, etc.) or free Edge TTS (`text_to_speech`).
- **Word Timings ("Computer listened back")**: Run local **`faster-whisper`** (`~/.hermes/cache/opt/whisper-venv/bin/python`, `base.en` with the PyAV `metadata_errors` shim, or `<home>/lemo-opuscar/.venv/bin/python`) over the generated TTS audio to emit `words.json` (`[{ "w": "...", "s": 1.24, "e": 1.58 }, ...]`).
- **Music & Foley**: We do **not** have ElevenLabs music/SFX generation. Synthesize deterministic procedural score + material-accurate foley via Python (`<home>/lemo-opuscar/core/audio/sfx.py` + `make_audio.py`) locked to exact `EDL.json` visual cues (`cuecheck.py` `< 5 ms`), mixed to **`-14.0 LUFS`**.
- **Visual Styles**: Choose from `<home>/SKILLS.md` (`<home>/lemo-skillsrc/styles/<slug>/STYLE.md` — 43 styles including `urban-sketch` for wobbly ink + watercolor, `blueprint`, `ink-wash`, `ukiyoe`, `midcentury-toon`, `rubber-hose` — plus `<home>/herk-edit-kit/MOTION_PHILOSOPHY.md`). No external AI image generators (`$0` picture cost).

---

## 3. Step-by-Step Execution Chain (`build/build.sh`)

1. **Research & Style Lock (Level 1 → Level 2)**:
   - Pick the matching `STYLE.md` from `<home>/SKILLS.md`.
   - Verify all factual claims and numbers from real sources; log them in `EDL.json` (`factual_verification`).
   - Write `TREATMENT.md` (logline, 3-act arc, style tokens, "one real thing" / signature move).
2. **Script & TTS Voice**:
   - Write spoken lines (`≤ 3.5 words/s`, `0.4–1.0s` inter-line breath, `1.0–1.5s` silence before the turn).
   - Generate `assets/voiceover.wav` with Kokoro ONNX or Edge TTS.
3. **Whisper Loopback (`words.json`)**:
   - Transcribe `assets/voiceover.wav` with `faster-whisper` (`word_timestamps=True`) to produce `words.json`.
4. **Word-Locked `EDL.json` / Storyboard (Level 3 Lock)**:
   - Bind every physical visual action (`action_cues`) to the exact `s` timestamp of its trigger word in `words.json` (e.g., `"struck"` → `14.28s`, `"chariot"` → `21.04s`).
   - Design at least one **continuous in-between state morph** per scene (e.g., rock → blade, drop → sea foam, flat plan → oblique extrusion) so nothing hangs static.
5. **Character & Anatomical Guardrails (Code-Drawn 2D)**:
   - **Parameterized rig functions**: Define each recurring character/object once (`drawCharacter(ctx, pose)`) so style and proportions stay 100% consistent across scenes.
   - **Cartoon-only anatomy**: Never draw realistic multi-joint human bodies or five-fingered hands in procedural JS (they look like stiff wooden dolls, and seated full-body figures "sit on a throne by standing on the seat"). Use **big heads, simple bodies, circle/mitten hands**, and frame around complex leg/hip bends (waist-up or foreground occlusion).
   - **Wide-shot scale floor**: Keep primary characters `≥ 18–25%` of canvas height even in wide shots so subjects never shrink to specks.
6. **Offscreen Texture Cache, Scene Culling & Stopwatch-Gated Render**:
   - Cache static procedural backgrounds (paper grain, watercolor washes, blueprint grids) to a single offscreen `<canvas>` (`paperC`) once at setup, draw active geometry directly onto `mainCtx` instead of blitting 3–4 full-screen scratch canvases per frame, gate each `drawSceneN(ctx, t)` by its active time window, and mux audio with `-c:v copy`.
   - Time every 20–30s batch against a **30–45s stopwatch window** (`~15–25 fps` capture floor; Binh rendered `3,708` frames / `123.6s` in `172s` = `21.6 fps`). Tested against our `1,152`-frame / `48s` blueprint film (`426.5s` render = `2.70 fps` / `177.7s` per 20s batch + `56.0s` mux re-encode), any batch exceeding **45s** (`< 10 fps`) immediately flags un-culled scene draws, multi-canvas full-frame blits, or a redundant `-c:v libx264` mux pass.
7. **Independent QA Gate**:
   - `npx hyperframes check` (0 errors).
   - `ffprobe` (video + audio streams, exact frame count and duration).
   - `ffmpeg blackdetect` (`0` black frames) + `loudnorm` (`-14.0 ± 1.0 LUFS`).
   - Extract and visually inspect `renders/contact_sheet.jpg` with vision (`Read`/`view_file`).
