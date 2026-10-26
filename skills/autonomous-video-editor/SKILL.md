---
name: autonomous-video-editor
description: "Use when editing a raw video into a polished cut."
version: 1.0.0
metadata:
  hermes:
    tags: [video, editing, captions, motion-graphics, ugc, hook, ffmpeg]
    category: creative
---

# Autonomous video editor (owner's Master Prompt)

The owner's standing contract for turning a RAW video into a finished, professional
short-form cut **without being told where to edit**. The verbatim prompt lives in
`references/master-prompt.md` — read it before editing and follow it exactly.

## When to Use

- Owner sends a raw video (talking head, screen recording, UGC) and asks to "edit it",
  "add camera movement / pop-ups / captions", or make a "hook" version.
- Any marketing/UGC cut where the brief is "make it look professionally edited".

## The contract (10 steps — never skip)

1. **Understand the video first** — analyse the ENTIRE video before cutting.
2. **Edit autonomously** — choose effects yourself; every edit must have a reason.
3. **Powerful hook** — the first 1–3 s is the most important part; no misleading clickbait.
4. **Context-aware edits** — SHOW what is being said (growth→graph, numbers→counters,
   website mentioned→UI visual, process→steps, gesture/click→transition trigger).
5. **Captions** — accurate, synced, varied treatment, emphasise key words. Never cover the face.
6. **Retention** — break long static stretches, but natural pacing beats constant motion.
7. **Sound design** — whooshes/pops/clicks/impacts/risers synced to visual actions; voice stays dominant.
8. **Preserve the original person** — never change face/identity/body/voice/lip-sync; no duplicates.
9. **Match the content style** — educational ≠ business ≠ tech ≠ comedy; choose the language.
10. **Do not over-edit** — no random zooms, no effect-per-second, no unrelated B-roll.

## Execution mapping (how the contract is actually delivered here)

Before editing, collect the delivery brief: raw video, destination platform, target duration, caption treatment (burned-in or separate), and brand/style constraints. If a Claude Code subscription lane is doing the orchestration, use the native subscription workflow in `autonomous-ai-agents/claude-code`; do not let inherited gateway variables silently route the run elsewhere.

Claude itself cannot render frames. The prompt is the **decision layer**; produce and
then execute an explicit EDL:

1. **Transcribe with word timings** — use the configured local or cloud transcriber and verify that the transcript exists before asking the editor to cut. For the Herk Edit Kit, `scripts/transcribe-elevenlabs.mjs` expects `ELEVENLABS_API_KEY` from the workspace secret mechanism; never paste or print the key. If transcription is unavailable, stop at the prerequisite gate instead of claiming an edited deliverable.
2. **Write the EDL as JSON** — a list of `{start, end, kind, params, reason}`, one row per
   edit (punch-in, caption group, graphic, b-roll, sfx, transition). The `reason` field is
   mandatory: it is the Step-2 "every edit must have a reason" guarantee and the audit trail.
3. **Render** with the existing stack — reuse `hyperframes-*` (composition/animation/audio),
   `general-video`, `embedded-captions`, `kinetic-multicam`; ffmpeg for cuts, punch-ins
   (scale+crop), speed changes, freeze frames and the audio bed. Vertical 9:16 unless told otherwise.
4. **Verify before delivering** — probe the output (duration, resolution, streams), confirm
   captions are burned and audio is present, and check the hook lands inside the first 3 s.
   Deliver the MP4 plus the EDL + a cost note.

## Hard rules distilled from real editor tutorials (adopt these; they beat taste)

- **Beat ceiling: no visual state may sit longer than 3 s** (target 1.5–3 s per beat), keyed to
  **word-level timestamps**, not fixed times. A static frame is the #1 retention killer.
- **Mask every hard cut.** Bridge each talking-head splice with a full-screen card/UI graphic so the
  cut reads as intentional instead of jarring.
- **Design system or it looks like AI slop.** Never let the model choose colours/type/spacing freely —
  it defaults to "generic AI vibe-coded" output. Feed explicit tokens (palette, type scale, spacing,
  card styling); see `references/design-system.md`.
- **Vector over raster** for all graphics: author SVG/HTML, not bitmaps — crisp at any scale and
  animatable element-by-element.
- **Motion physics:** entrances ease-in with a tiny overshoot, then settle. No abrupt pops, no plain
  fades. Transform-only (scale/translate/opacity) — never animate `left`/`top` (integer snapping stutters).
- **Audio space:** leave ~50–100 ms of pre-roll before speech so the first consonant never clips, and
  insert ~2 s of quiet after a demonstration beat so a graphic can play without narration over it.
- **Separate audio stems** (music / ambience / SFX) — never bake SFX into the music; normalise the mix
  to about **−14 LUFS**. SFX land on the visual in-point of the element they support.
- **Retake trimming:** keep only the LAST clean take of a repeated line; drop restarts, stumbles,
  coughs and dead air.
- **80/20 rule:** a single zero-shot pass reaches ~80%. Production grade needs an explicit
  review → fix loop. Budget for it; never ship the first render.
- **Never invent a number.** Every on-screen statistic must come from the supplied script/website.
  A fabricated figure (e.g. "87 websites" when the script says 649) is a ship-blocker.
- **Action-on-word binding ("the blade moves on *struck*, not near it, on it"):** For code-drawn animations and motion callouts alike, run `faster-whisper` even on locally synthesized TTS audio so `words.json` has the exact second of every spoken word, and fire the visual action on that exact word timestamp (`words[i].s`) rather than a coarse sentence window. *Why:* sentence-level timing leaves visual hits drifting 0.3–1.5s off the spoken trigger verb.
- **Cartoon-only code-drawn anatomy & parameterized rigs:** When drawing characters in JS/Canvas/SVG instead of cutting camera footage, author one reusable function (`drawCharacter(ctx, pose)`) with cartoon proportions (big head, simple body, circle hands), plan framing around unbendable leg/hip bends, and keep subjects `≥ 18–25%` of canvas height in wide shots. *Why:* per-shot regeneration drifts character identity, realistic multi-joint human limbs in procedural 2D JS look like stiff wooden dolls ("sitting on a throne by standing on the seat"), and unguarded wide shots shrink characters to unreadable specks.

## Render economics (measured on this VPS, software GPU — plan budgets around it)

A 49.7 s 1080×1920 composition: **~1 m 35 s for a simple overlay-only build, ~2 m 21 s for a full
variant** (22 beats + 4 B-roll videos + captions + SFX), at `-q draft` with `--workers 2`; roughly
double for `-q delivery`. Time is **capture-bound** (headless Chrome in `beginframe` mode: 2 m 11 s of
a 2 m 21 s run), not encode-bound; peak RSS ≈ 380 MB, software GPU. So a two-variant delivery is a
~6 minute job, and render time is **free** — the money is in model tokens and any generated footage.

- **The 30–45s Batch Stopwatch Rule (`~15–25 fps` floor):** Time every 20–30s render batch (`600–900` frames) against a **30–45s wall-clock window** (external benchmark: `3,708` frames / `123.6s @ 30fps` in `172s` = `21.6 fps` at `$0` picture spend vs `$0.72` for 231 still AI images; internal test on our `1,152`-frame / `48s @ 24fps` blueprint film: `426.5s` capture/encode = `2.70 fps` / `177.7s` per 20s batch + `56.0s` redundant mux re-encode). If a 20–30s batch exceeds **45s** (`< 10 fps`), a per-frame or mux bottleneck exists — check for un-culled scene functions running every frame, multiple full-screen (`1080×1920`) offscreen canvas clears/blits or un-cached procedural noise per frame, and always use `-c:v copy` (never a second `-c:v libx264` pass) when muxing calibrated master audio. *Why:* timing a short batch with a stopwatch catches `2.7 fps` draw-loop stalls before committing to a long render that hits the task timeout.

**Keep only the final render in `renders/`.** Intermediate drafts are indistinguishable from the
deliverable by filename alone; archive them to `renders/_superseded/` or delete them, so nobody ships
the broken take.

## QA gate — run this BEFORE showing anyone (script it, don't eyeball it)

1. `npx hyperframes lint` (0 errors) and `npx hyperframes check`.
2. **Contact sheet**: `ffmpeg -i out.mp4 -vf "fps=1,scale=320:-1,tile=8x8" sheet.jpg` — inspect for text
   overflow, off-frame elements, empty/black frames, low contrast.
3. **Render verification** (`ffprobe`): expected resolution · duration matches the timeline to the frame ·
   an audio stream is present · **black-frame count = 0**.
4. Only then deliver, together with the EDL and the raw gate output.

## HyperFrames-specific traps (each one shipped a visibly broken frame before it was caught)

- **A caption group must be a TIMED element** (`data-start`/`data-duration`). Wrapping all groups in one
  full-length clip and animating their opacity with GSAP leaves every group visible at once — the last
  line then sits over the entire video. Timed clips are hidden by the framework; GSAP is only polish.
- **Words need a CSS `opacity: 0` start**, or they are all visible before their cue.
  Tween only to opacity 1 (`fromTo(el, {y:14}, {y:0, opacity:1, ...}, wordStart)`).
- **Never show a caption and a designed card carrying the same words.** Drop any caption group whose
  window falls inside a card's window.
- **ASR breaks tokens.** Merge `plus/919/-453/-7933.` → `[REDACTED_PHONE]` and `ROI/in/FOTEC/.com` →
  `roiinfotech.com` before rendering captions, or the phone number displays as `+91 [REDACTED_PHONE]`.
- **`renders/` is gitignored; `variants/` is not** — add working-media paths to `.gitignore` before
  committing a video project.
- Verify by **looking at frames**, not by lint: `ffmpeg -i out.mp4 -vf "fps=1/4,scale=300:-1,tile=4x3" sheet.jpg`
  and inspect. Lint reported 0 errors on a render whose captions were wrong.

## Pitfalls

- **Do not over-edit** (Step 10) — the most common failure. Fewer, motivated edits win.
- **A worker that ends its turn waiting on an async render has burned the run.** Render in the
  FOREGROUND and wait for the file; never hand off and return (observed: Sonnet produced no output at all).
- **Local CPU Whisper is slow** (15–50 min per hour of audio). Long inputs → a cloud STT route.
- **Freeform "generate the whole video from a prompt" is the expensive, unreliable path** — build a
  FIXED template/composition and vary its data. Both the tutorials and our own A/B agree.
- **Never regenerate or morph the speaker's face/voice** (Step 8) — cuts, zooms, masks and
  graphics only.
- **Captions must never cover the face** — plan caption placement from the framing, not a default bar.
- **Sound design must not bury the voice** — mix dialogue dominant, SFX under it.
- **The hook is judged in the first 1–3 seconds** — if the opening is a slow intro, restructure it.
- A raw video's own audio IS the narration; only add music/SFX under it, never replace the voice.
