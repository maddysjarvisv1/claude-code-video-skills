---
name: ultron-video-pipeline
description: "Run Ultron's generative 10-stage brief-to-Discord video pipeline (code-drawn visuals by default)."
version: 0.2.0
author: Jarvis, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, ultron, hyperframes, pipeline, generative-graphics, motion-graphics, animation, captions]
    category: creative
    related_skills: [memory-architecture]
---

# Ultron Video Pipeline Skill

End-to-end operating procedure for the `vid` ("Ultron") creator profile. Turns a one-line video request into a researched, scripted, **code-generated** (`HTML/SVG/Canvas2D/WebGL/Manim/Remotion`), captioned, audio-mastered, verified MP4 delivered to Discord `#content-pipeline` (`[REDACTED_PHONE]`), reusing the workspace's graphics, motion, writing, and audio skills rather than reinventing them.

> **HARD RULES & LIMITS:**
> 1. **Never spend full-reel render time before the hook and outline are approved by the owner** (unless the owner explicitly delegated autonomous sign-off with *"you decide"*).
> 2. **GENERATE THE VISUALS IN CODE.** Every Ultron video is built in code — motion graphics, animated diagrams, data visualisation, kinetic typography, vector transitions, shapes, and particles using the graphics/motion skill family. Generated visuals are the backbone; they need no licence record because they are ours. A video that is only stock footage or a slideshow of stills is not an Ultron video and is not acceptable.
> 3. **Never download, rip, or re-cut a third-party video.** No YouTube, Vimeo, or social platform video fetching, and no reaction or re-cutting someone else's footage. This host is IP-blocked by YouTube anyway, and the rights problem is worse than the technical one. It is permanently out of scope by owner decision (`[REDACTED_PHONE]`).
> 4. **Supporting assets are OPTIONAL, never load-bearing.** Licensed stills, music, and SFX may support a code-generated piece (free/CC only, with exact source page and licence recorded in `assets_ledger.json`).

## When to Use

- The owner or Jarvis asks Ultron (`vid`) to generate, animate, or produce a video from a topic, brief, URL, GitHub PR, music track, or PDF using procedural graphics and motion built in code.
- Resuming an in-progress generative video project at any stage from `(0) INTAKE` through `(9) DELIVER`.
- Auditing a finished render against Ultron's pre-delivery verification gates ([`references/verification.md`](references/verification.md)) and optional supporting-asset licence ledger (`scripts/asset_ledger.py`).
- **Don't use for:** Downloading or re-cutting third-party videos (permanently forbidden), external or client-facing social uploads (requires owner approval via Jarvis), mutating `brain.db`, or non-video software engineering tasks.

## Prerequisites

- **Tools:** Hermes `read_file`, `write_file`, `patch`, `search_files`, `terminal`, `web_search`, `web_extract`, `vision_analyze`, `delegate_task`.
- **Helper scripts:**
  - `scripts/corpus_index.py` — SQLite FTS5 indexer and search CLI over Ultron's 5 authorized corpus roots (withholds `.env`, `*token*`, and secret patterns).
  - `scripts/asset_ledger.py` — fail-closed provenance and licence ledger CLI (`add`, `verify`, `list`) for **optional supporting stills, music, and SFX** (generated code visuals need no licence entry because they are ours).
- **Disclosed references (load at the stage that needs them):**
  - Stage 1 questions & defaults: [`references/intake-questions.md`](references/intake-questions.md)
  - Stage 2 corpus roots & PDF mining: [`references/corpus.md`](references/corpus.md)
  - Stage 4 optional supporting-asset licence rules: [`references/asset-sourcing.md`](references/asset-sourcing.md)
  - Stage 8 pre-delivery verification gate: [`references/verification.md`](references/verification.md)

## Existing Skills to Reuse (Never Reinvent)

Load the frontmatter/body of the owning skill via `read_file` when entering its stage:

| Capability | Existing Skills to Load |
|---|---|
| **Entry point & workflow routing** | [`hyperframes`](../../hyperframes/SKILL.md) (mandatory entry point for HTML-to-video routing), [`motion-graphics`](../../motion-graphics/SKILL.md), [`faceless-explainer`](../../faceless-explainer/SKILL.md), [`product-launch-video`](../../product-launch-video/SKILL.md), [`music-to-video`](../../music-to-video/SKILL.md), [`pr-to-video`](../../pr-to-video/SKILL.md), [`website-to-hyperframes`](../../herk/website-to-hyperframes/SKILL.md), [`slideshow`](../../slideshow/SKILL.md) |
| **HyperFrames domain modules** | [`hyperframes-core`](../../hyperframes-core/SKILL.md), [`hyperframes-animation`](../../hyperframes-animation/SKILL.md), [`hyperframes-keyframes`](../../hyperframes-keyframes/SKILL.md), [`hyperframes-creative`](../../hyperframes-creative/SKILL.md), [`hyperframes-audio`](../../hyperframes-audio/SKILL.md), [`hyperframes-cli`](../../hyperframes-cli/SKILL.md), [`hyperframes-registry`](../../hyperframes-registry/SKILL.md), [`hyperframes-studio`](../../hyperframes-studio/SKILL.md), [`creative/hyperframes-video-production`](../hyperframes-video-production/SKILL.md), [`hyperframes-video-beats`](../../herk/hyperframes-video-beats/SKILL.md), [`gsap`](../../herk/gsap/SKILL.md) |
| **Code animation & generative engines** | [`creative/remotion-video`](../remotion-video/SKILL.md) (React/Remotion), [`creative/manim-video`](../manim-video/SKILL.md) (3Blue1Brown math/algo diagrams), [`creative/p5js`](../p5js/SKILL.md) (canvas/WebGL/shaders/particles), [`creative/animate`](../../animate/SKILL.md) (single-file procedural canvas), [`creative/ascii-video`](../ascii-video/SKILL.md) (colored ASCII MP4/GIF) |
| **Research, PDFs & owned transcripts** | [`productivity/pdf`](../../productivity/pdf/SKILL.md) (`pdf_read.py`, `extract_pymupdf.py`), [`youtube-content`](../../media/youtube-content/SKILL.md) (scripts and pacing from an existing transcript you own — never download third-party video) |
| **Script structure & voice** | [`writing-beats`](../../writing-beats/SKILL.md) (grounding concepts beat-by-beat), [`writing-shape`](../../writing-shape/SKILL.md) (shaping raw notes into prose), [`humanizer`](../humanizer/SKILL.md) (strip AI-isms so lines survive being read aloud) |
| **Audio & optional supporting media** | [`media/songsee`](../../media/songsee/SKILL.md) (spectrograms, mel/chroma/MFCC beat features), [`creative/songwriting-and-ai-music`](../songwriting-and-ai-music/SKILL.md), [`media-use`](../../media-use/SKILL.md) (local TTS, transcription, optional licensed supporting stills/audio) |
| **Editing, storytelling, design & captions** | [`video-storytelling`](../../herk/video-storytelling/SKILL.md) (persistent visual world, camera grammar), [`short-form-edit`](../../herk/short-form-edit/SKILL.md) (retention pacing, beat cuts, SFX timing), [`embedded-captions`](../../embedded-captions/SKILL.md) (burned-in or anchor-rail captions), [`creative/design-tokens`](../design-tokens/SKILL.md), [`creative/popular-web-designs`](../popular-web-designs/SKILL.md), [`creative/claude-design`](../claude-design/SKILL.md) |

## How to Run

Execute all CLI helpers through the `terminal` tool:

```bash
# 1. Index and search the workspace corpus (Stage 2)
python3 scripts/corpus_index.py build --json
python3 scripts/corpus_index.py search "<topic query>" --limit 10 --json

# 2. Render & motion-check the Stage 4 sample scene (Stage 4 proof artefact)
npx hyperframes render <project>/scenes/scene-01 --fps 30 -q high -o <project>/renders/scenes/scene-01-sample.mp4
ffmpeg -v error -i <project>/renders/scenes/scene-01-sample.mp4 -vf "freezedetect=n=-60dB:d=0.5" -f null - 2>&1

# 3. OPTIONAL: Record and verify supporting stills/music/SFX licences (only when optional assets are used)
python3 scripts/asset_ledger.py add \
  --ledger <project>/assets_ledger.json \
  --local-path "assets/diagram.svg" \
  --source-url "https://commons.wikimedia.org/wiki/File:Transformer_architecture.svg" \
  --licence "CC-BY-SA-4.0" \
  --author "Wikimedia Contributor" \
  --used-in "scene-02 (00:08-00:14)"

python3 scripts/asset_ledger.py verify \
  --ledger <project>/assets_ledger.json \
  --assets-dir <project>/assets
```

## Quick Reference — The 10 Stages

| Stage | Name | Proof Artefact on Disk | Stop & Ask Gate |
|---|---|---|---|
| `(0)` | **INTAKE** | `<project>/INTAKE.json` | Stop immediately if the request has zero identifiable subject or attempts to download/re-cut a third-party video. |
| `(1)` | **CLARIFY** | `<project>/BRIEF.md` | **MUST STOP** and ask `<= 7` batched questions from [`references/intake-questions.md`](references/intake-questions.md) unless already answered or owner said *"you decide"*. |
| `(2)` | **RESEARCH** | `<project>/RESEARCH.md` | Stop if an owner-specified source URL/PDF is unreadable or contradicts the core premise. |
| `(3)` | **SCRIPT + HOOK** | `<project>/SCRIPT.md` | **MUST STOP** to get owner approval on the 3-second hook + beat outline before full-reel rendering (unless combined with Stage 5 gate or owner said *"you decide"*). |
| `(4)` | **GENERATE VISUALS** | `<project>/STORYBOARD.md` + rendered sample scene (`<project>/renders/scenes/scene-01-sample.mp4`) | **HARD GATE** — stop if the sample scene has any static frame where motion was promised, or if an optional supporting still/music/SFX asset lacks a valid free/CC licence. |
| `(5)` | **STORYBOARD + Approval Gate** | `<project>/STORYBOARD.md` + `<project>/EDL.json` + sample scene proof | **HARD GATE — MUST STOP** for owner sign-off on hook, outline, storyboard, and sample scene before Stage 6 (`BUILD/ANIMATE`). |
| `(6)` | **BUILD / ANIMATE** | `<project>/index.html` (or `scenes/scene-NN/`) + `<project>/build-check.log` | Stop if multi-scene build hits a blocker or exceeds the 30–45s per-batch render stopwatch ceiling (`< 10 fps`). |
| `(7)` | **EDIT + CAPTIONS** | `<project>/renders/final.mp4` + `.srt` | Stop only if audio mastering or caption sync fails after automated repair. |
| `(8)` | **VERIFY** | `<project>/VERIFY-REPORT.md` | **HARD GATE** — automatic FAIL on any static frame where motion was promised, stock-only visuals, or any unlicensed supporting asset; fix before Stage 9. |
| `(9)` | **DELIVER** | `<project>/DELIVERY.json` + Discord message in `#content-pipeline` | Stop before any external/client publishing (owner via Jarvis required). |

---

## Procedure (Stages 0–9)

### Stage (0) INTAKE

- **Inputs:** Raw user brief (one-line prompt, topic, website URL, GitHub PR, PDF path, or music track) + existing project directory state.
- **Action:**
  1. Reject immediately if the request asks to download, rip, or re-cut a third-party video (permanently out of scope by owner decision `[REDACTED_PHONE]`; offer to generate an original code-drawn explainer on the topic instead).
  2. Check project state following [`hyperframes`](../../hyperframes/SKILL.md) § 1 (`BRIEF.md`, `STORYBOARD.md`, or `hyperframes.json` already on disk).
  3. Create `<project>/` workspace directory and write `<project>/INTAKE.json` recording `request_text`, `input_paths`, `detected_route` (e.g. `motion-graphics`, `faceless-explainer`, `product-launch-video`, `website-to-hyperframes`, `pr-to-video`, `music-to-video`, `slideshow`, `manim-video`, `remotion-video`, `p5js`, `animate`, `ascii-video`), and `timestamp`.
- **Outputs:** Initialized project folder and generative route selection.
- **Artefact:** `<project>/INTAKE.json` (non-empty JSON with `request_text` and `detected_route`).
- **Stop & Ask Gate:** Stop immediately if the prompt names neither a subject nor an input file/URL, or if it asks to fetch/re-cut third-party video.

### Stage (1) CLARIFY

- **Inputs:** `<project>/INTAKE.json` and [`references/intake-questions.md`](references/intake-questions.md).
- **Action:**
  1. Read [`references/intake-questions.md`](references/intake-questions.md). Diff the output-changing dimensions (length, platform/aspect, audience, tone, own research vs owner sources, deadline, voiceover, caption style, and generative visual style/brand) against what the owner already stated.
  2. Batch all missing dimensions into **one single list of at most 7 questions** verbatim from [`references/intake-questions.md`](references/intake-questions.md).
  3. If the owner replies *"you decide"*, apply the **Default Assumptions** table from [`references/intake-questions.md`](references/intake-questions.md) and record every assumed value under `## Stated Assumptions` in `<project>/BRIEF.md`.
- **Outputs:** Locked production parameters (`target_duration_sec`, `aspect_ratio`, `resolution`, `audience`, `tone`, `research_mode`, `deadline`, `voiceover`, `caption_style`, `style_slug`, `brand_tokens`).
- **Artefact:** `<project>/BRIEF.md` containing all locked parameters and `## Stated Assumptions`.
- **Stop & Ask Gate:** **MUST STOP** and present the single batched question list before proceeding whenever any output-changing parameter is unspecified and the owner has not said *"you decide"*.

### Stage (2) RESEARCH

- **Inputs:** `<project>/BRIEF.md` and [`references/corpus.md`](references/corpus.md).
- **Action:**
  1. Read [`references/corpus.md`](references/corpus.md). Run `terminal(command="python3 scripts/corpus_index.py search \"<query>\" --json")` to mine `[REDACTED_PATH]`, `[REDACTED_PATH]`, `[REDACTED_PATH]`, `[REDACTED_PATH]`, and `[REDACTED_PATH]`.
  2. Read any relevant existing PDFs using [`productivity/pdf`](../../productivity/pdf/SKILL.md) (`pdf_read.py` / `extract_pymupdf.py`) and any existing transcripts you own using [`youtube-content`](../../media/youtube-content/SKILL.md) (for script structure and pacing only — never download third-party video).
  3. Run primary-source web verification via `web_search` and `web_extract` when `research_mode` includes Ultron research.
  4. Compile `<project>/RESEARCH.md` with a claim-to-source citation table (local `file://` path or exact primary URL for every fact/stat).
- **Outputs:** Verified fact sheet and citation list.
- **Artefact:** `<project>/RESEARCH.md` with `>= 1` verified citation per factual claim and zero unsourced claims.
- **Stop & Ask Gate:** Stop and ask the owner if an owner-supplied source URL/PDF is inaccessible or if primary sources directly refute the requested premise.

### Stage (3) SCRIPT + HOOK

- **Inputs:** `<project>/BRIEF.md`, `<project>/RESEARCH.md`, [`writing-beats`](../../writing-beats/SKILL.md), [`writing-shape`](../../writing-shape/SKILL.md), [`humanizer`](../humanizer/SKILL.md).
- **Action:**
  1. Ground concepts in order using [`writing-beats`](../../writing-beats/SKILL.md) and shape prose using [`writing-shape`](../../writing-shape/SKILL.md).
  2. Draft the **first-3-seconds hook** (curiosity gap, sharp contrast, or concrete stake in `<= 12` words), the beat-by-beat spoken script timed to `target_duration_sec` (~2.5 words/sec), and an ending that earns the watch.
  3. Pass every spoken line through [`humanizer`](../humanizer/SKILL.md): strip AI filler (*"in today's fast-paced world"*, *"delve into"*, *"testament to"*). Read every sentence aloud mentally — if a human speaker would stumble, rewrite it.
- **Outputs:** Spoken script with hook, beat timings, and citation anchors.
- **Artefact:** `<project>/SCRIPT.md` containing `## Hook (0:00-0:03)`, `## Beat Outline`, and `## Full Spoken Script`.
- **Stop & Ask Gate:** **MUST STOP** and show the hook + outline to the owner before spending full-reel render time (may be presented together with the Stage 4 sample scene and Stage 5 storyboard packet so the owner approves once before Stage 6).

### Stage (4) GENERATE VISUALS

- **Inputs:** `<project>/BRIEF.md`, `<project>/SCRIPT.md`, [`motion-graphics`](../../motion-graphics/SKILL.md), [`hyperframes-animation`](../../hyperframes-animation/SKILL.md), [`hyperframes-keyframes`](../../hyperframes-keyframes/SKILL.md), [`gsap`](../../herk/gsap/SKILL.md), [`creative/manim-video`](../manim-video/SKILL.md), [`creative/p5js`](../p5js/SKILL.md), [`creative/animate`](../../animate/SKILL.md), [`creative/remotion-video`](../remotion-video/SKILL.md), [`creative/ascii-video`](../ascii-video/SKILL.md), and (for optional supporting assets only) [`references/asset-sourcing.md`](references/asset-sourcing.md).
- **Action:**
  1. **Design every scene as code-generated graphics (the mandatory backbone):**
     - Map each beat in `<project>/SCRIPT.md` to a concrete procedural visual in `<project>/STORYBOARD.md`: motion graphics cards (`editorial-collage`, `kallaway-glass`, `bento-grid`, `neo-brutal`, `youtube-clean`), animated SVG architecture diagrams, live data visualisations (bar/line/counter charts), kinetic vector typography, GSAP/keyframe state transitions, or Canvas2D/WebGL particle fields.
     - **Generated visuals need no licence record because they are ours.** Every word, number, badge, and callout on screen is drawn as deterministic DOM/SVG/Canvas2D vector graphics.
  2. **Build and render a sample scene (`scene-01-sample.mp4`) in code:**
     - Author the hook/opening scene (`<project>/scenes/scene-01/index.html` or engine equivalent) and render `<project>/renders/scenes/scene-01-sample.mp4`.
     - Verify the sample scene has continuous state transformation (zero frozen frames via `freezedetect` and visual check via `vision_analyze`).
  3. **OPTIONAL supporting assets (licensed stills, music, and SFX — never load-bearing):**
     - A video that is only stock footage or a slideshow of stills is **not** an Ultron video and is rejected at verification.
     - You may synthesize local TTS voiceover (`assets/narration.ogg` / `assets/master_audio.wav`) and procedural SFX (`sfx.py`), or include optional free/CC supporting stills, music, or SFX. For music-driven timing, extract beat features with [`media/songsee`](../../media/songsee/SKILL.md).
     - Whenever any third-party still, music track, or SFX file is placed in `<project>/assets/`, record its exact item page `source_url`, `licence`, `author`, and `used_in` in `<project>/assets_ledger.json` via `scripts/asset_ledger.py add` and verify with `scripts/asset_ledger.py verify` (see [`references/asset-sourcing.md`](references/asset-sourcing.md)).
- **Outputs:** Visual storyboard mapping every scene to code-drawn graphics, a rendered and verified sample scene clip, and (if optional supporting assets are used) a verified `assets_ledger.json`.
- **Artefact:** `<project>/STORYBOARD.md` + `<project>/renders/scenes/scene-01-sample.mp4` (non-empty MP4 passing `freezedetect` with zero static frames where motion was promised; plus `<project>/assets_ledger.json` when optional supporting stills/music/SFX are present).
- **Stop & Ask Gate:** **HARD GATE** — stop if `<project>/renders/scenes/scene-01-sample.mp4` fails to render or contains a static frame where motion was promised; if optional supporting stills/music/SFX are used, stop if any asset fails `scripts/asset_ledger.py verify` and cannot be replaced with code-drawn graphics or a licensed free/CC file.

### Stage (5) STORYBOARD + Approval Gate

- **Inputs:** `<project>/BRIEF.md`, `<project>/SCRIPT.md`, `<project>/STORYBOARD.md`, `<project>/renders/scenes/scene-01-sample.mp4`, [`video-storytelling`](../../herk/video-storytelling/SKILL.md), [`hyperframes-creative`](../../hyperframes-creative/SKILL.md), [`hyperframes-video-beats`](../../herk/hyperframes-video-beats/SKILL.md).
- **Action:**
  1. If narrated, run `faster-whisper` over the local TTS/voiceover audio to produce word-locked timestamps in `<project>/words.json` (Level 3 lock per [`creative/hyperframes-video-production`](../hyperframes-video-production/SKILL.md)).
  2. Lock the scene-by-scene choreography using [`video-storytelling`](../../herk/video-storytelling/SKILL.md) and [`hyperframes-creative`](../../hyperframes-creative/SKILL.md). Bind every code-drawn visual entrance, chart/diagram morph, camera move, transition handoff, and SFX hit to exact word seconds in `<project>/EDL.json` and `<project>/STORYBOARD.md`, and export `sfx-cues.md` / `sfx-cues.csv`.
  3. Present the **Hook + Outline + Storyboard + Rendered Sample Scene (`scene-01-sample.mp4`)** (and any stated assumptions) to the owner.
- **Outputs:** Word-locked edit decision list, finalized scene storyboard, and sample scene preview ready for owner sign-off.
- **Artefact:** `<project>/STORYBOARD.md` + `<project>/renders/scenes/scene-01-sample.mp4` (and `<project>/EDL.json` + `<project>/words.json` for narrated pieces).
- **Stop & Ask Gate:** **HARD APPROVAL GATE — MUST STOP.** Never enter Stage 6 (`BUILD/ANIMATE` full-reel rendering) until the owner approves the hook, outline/storyboard, and sample scene (unless the owner already gave explicit *"you decide"* sign-off for an autonomous run).

### Stage (6) BUILD / ANIMATE

- **Inputs:** Approved `<project>/STORYBOARD.md`, `<project>/EDL.json`, `<project>/renders/scenes/scene-01-sample.mp4` (and optional `<project>/assets_ledger.json`).
- **Action:**
  1. Select the generative animation engine matched in `BRIEF.md`:
     - **HyperFrames + Motion Graphics (default):** Load [`motion-graphics`](../../motion-graphics/SKILL.md), [`hyperframes-core`](../../hyperframes-core/SKILL.md), [`hyperframes-animation`](../../hyperframes-animation/SKILL.md), [`hyperframes-keyframes`](../../hyperframes-keyframes/SKILL.md), [`gsap`](../../herk/gsap/SKILL.md), [`hyperframes-registry`](../../hyperframes-registry/SKILL.md), and [`hyperframes-cli`](../../hyperframes-cli/SKILL.md) (or [`slideshow`](../../slideshow/SKILL.md)). Build isolated per-scene compositions (`scenes/scene-01` .. `scenes/scene-NN`), wire seek-safe GSAP/CSS/SVG/Canvas2D timelines, validate with `npx hyperframes check`, and render `renders/scenes/scene-NN-v1.mp4`.
     - **Remotion (React):** Load [`creative/remotion-video`](../remotion-video/SKILL.md).
     - **Manim (math/algorithms):** Load [`creative/manim-video`](../manim-video/SKILL.md).
     - **p5.js / shaders / generative canvas:** Load [`creative/p5js`](../p5js/SKILL.md) or [`creative/animate`](../../animate/SKILL.md).
     - **ASCII terminal art:** Load [`creative/ascii-video`](../ascii-video/SKILL.md).
  2. For large builds (`> 60s` multi-scene code films), dispatch to Ag2 (`gemini-4-argon-high`, 2 h ceiling) with a `JOB/GOAL/SKILLS/MODEL` brief per Ultron's `SOUL.md`.
  3. Record SHA-256 checksums (`renders/scenes/sha256-v1.txt`) so any future single-scene revision re-renders only `scene-0K-v2.mp4` while keeping untouched scenes byte-identical.
  4. Ensure continuous visual motion or purposeful state transformations in every scene — never leave a dead static canvas.
- **Outputs:** Validated composition code (`0` lint/check errors) and isolated scene renders (`renders/scenes/scene-NN-v1.mp4`).
- **Artefact:** `<project>/index.html` (or `scenes/scene-NN/` source tree) + passing validation log (`<project>/build-check.log`).
- **Stop & Ask Gate:** Stop and report status if the build blocks on a missing dependency, exceeds the 30–45s batch render stopwatch ceiling (`< 10 fps`), or requires scope adjustment.

### Stage (7) EDIT + CAPTIONS

- **Inputs:** Rendered scene clips (`renders/scenes/scene-NN-v1.mp4`), `<project>/words.json`, optional `<project>/assets_ledger.json`, [`short-form-edit`](../../herk/short-form-edit/SKILL.md), [`embedded-captions`](../../embedded-captions/SKILL.md), [`hyperframes-audio`](../../hyperframes-audio/SKILL.md).
- **Action:**
  1. Concatenate isolated scene renders (`ffmpeg -f concat -safe 0 -c:v copy`), cut dead air, and align scene transitions to the beat or spoken word timestamps ([`short-form-edit`](../../herk/short-form-edit/SKILL.md)).
  2. Mix audio tracks via [`hyperframes-audio`](../../hyperframes-audio/SKILL.md) or `ffmpeg`: carve/duck any optional music bed under voiceover (`-18` to `-22 LUFS`, cutting `0.5s` before the final payoff line), place SFX cues at exact `EDL.json` timestamps, and master integrated loudness to `-14.0 LUFS` with true peak `< -0.1 dBFS`.
  3. Burn in or attach sidecar captions (`.srt` / `.vtt`) synced to `<project>/words.json` using [`embedded-captions`](../../embedded-captions/SKILL.md).
  4. Render the final mastered container to `<project>/renders/final.mp4`.
- **Outputs:** Mastered MP4 with mixed audio and synced captions.
- **Artefact:** `<project>/renders/final.mp4` (and `<project>/renders/final.srt` when captions are enabled).
- **Stop & Ask Gate:** Stop only if transcription/caption alignment or audio mastering fails after automated retry.

### Stage (8) VERIFY

- **Inputs:** `<project>/renders/final.mp4`, `<project>/STORYBOARD.md`, optional `<project>/assets_ledger.json`, [`references/verification.md`](references/verification.md).
- **Action:**
  1. Load and execute every check in [`references/verification.md`](references/verification.md):
     - Confirm `<project>/renders/final.mp4` exists and record its exact path and byte size (`stat -c "%n %s"`).
     - **WATCH the video:** extract frames across every scene and motion window and inspect them with `vision_analyze`. Confirm the visual backbone is code-generated graphics (never stock-only footage or a static slideshow).
     - Run `freezedetect` / consecutive frame diff across every scene that promised motion. **A static frame where motion was promised is an automatic FAIL.**
     - Verify container duration via `ffprobe` matches `BRIEF.md` bounds.
     - Verify audio stream presence, `-14 LUFS` loudness window, and zero clipping (`max_volume < -0.1 dBFS`).
     - Verify captions are present, legible inside safe zones, and synced within `<= 100ms`.
     - If optional supporting assets exist in `<project>/assets/`, run `python3 scripts/asset_ledger.py verify --ledger <project>/assets_ledger.json --assets-dir <project>/assets` (must exit `0`).
  2. Write `<project>/VERIFY-REPORT.md`. If any check fails, return to Stage 6 or Stage 7, fix the defect, re-render only the affected scene(s), and re-run Stage 8 from scratch.
- **Outputs:** Signed-off verification report with measured values.
- **Artefact:** `<project>/VERIFY-REPORT.md` with all 7 checklist items marked `PASS`.
- **Stop & Ask Gate:** **HARD QUALITY GATE** — never proceed to Stage 9 (`DELIVER`) while any item in `VERIFY-REPORT.md` is `FAIL`.

### Stage (9) DELIVER

- **Inputs:** `<project>/renders/final.mp4`, `<project>/VERIFY-REPORT.md`, `<project>/RESEARCH.md`, `<project>/BRIEF.md`, optional `<project>/assets_ledger.json`.
- **Action:**
  1. Post the finished `<project>/renders/final.mp4` to Discord **#content-pipeline** (`[REDACTED_PHONE]`) with a concise delivery note containing:
     - Exact file path and byte size
     - Duration, dimensions (`<width>x<height>`), aspect ratio, and frame rate
     - Generative style & graphics engine used (`hyperframes` / `motion-graphics` style slug, Manim, p5.js, etc.)
     - Caption format (burned-in style and/or `.srt` sidecar)
     - Stated assumptions (if the owner said *"you decide"* in Stage 1)
     - Supporting asset licences (`Generated in code (ours — no external licence needed)` plus `python3 scripts/asset_ledger.py list --ledger <project>/assets_ledger.json` if optional stills/music/SFX were used)
     - Research citations used from `<project>/RESEARCH.md`
  2. Write `<project>/DELIVERY.json` recording the delivery timestamp, file path, byte size, and Discord channel/message metadata.
- **Outputs:** Delivered video in `#content-pipeline` (`[REDACTED_PHONE]`) and delivery receipt.
- **Artefact:** `<project>/DELIVERY.json`.
- **Stop & Ask Gate:** **HARD BOUNDARY** — `#content-pipeline` is internal. Stop and ask the owner (via Jarvis) before any external upload, social media post, or client-channel publication.

---

## Recipe: Build a Full 2–3 Minute Generative Video (10-Scene Blueprint)

This is the canonical pattern for turning a brief like *"generate me a 2.5-minute video on why AI model routing beats single-model monoliths"* into a finished `150.0s` (`2m 30s`, `16:9` `1920x1080 @ 30fps`) code-drawn film.

### How the Hook Lands (First 3 Seconds) & How Scenes Hand Off

- **First 3 seconds (`0:00–0:03`, Scene `S01`):** Zero throat-clearing, zero logo fade-in. Frame `0` opens on a high-contrast `neo-brutal` split card where a live cost counter spins upward while the 10-word spoken hook lands: *"Ninety percent of your AI spend is paying a genius to sort mail."* On the word *"sort"* (`2.10s`), a crimson stamp slams onto the monolith block and fractures it into three routed lanes.
- **Scene-to-scene handoffs:** Every scene ends with an active vector element (a badge, a connector line, a morphing bar, or a camera pan) whose final frame geometry anchors the opening frame of the next scene, paired with a deterministic SFX cue (`swoosh`, `click`, `sub-drop`) locked to `words.json`.

### 10-Scene Plan (`150.0s` / `2m 30s` Total)

| Scene | Time (`s`) | Beat & Spoken Purpose | Visual Idea (Graphics Skill & Code Primitive) | On-Screen Vector Text | Scene Handoff Choreography |
|---|---|---|---|---|---|
| `S01` | `0:00–0:03` (`3.0s`) | **The Hook:** Shock the viewer with the cost/latency waste of sending trivial prompts to frontier models. | **`motion-graphics` (`neo-brutal`) + `gsap`:** High-voltage yellow card (`#FACC15`) with thick black ink border; oversized ticker rolls `$0.00 → $14,200/mo` while a frontier monolith block strains under tiny envelope icons. | `90% OF AI SPEND = OVERKILL` / `$14,200 / MO` | On spoken word *"mail"* (`2.75s`), the monolith block splits along a 3-way SVG path that extends rightward into `S02`'s dark canvas. |
| `S02` | `0:03–0:18` (`15.0s`) | **The Monolith Bottleneck:** Show how one giant model queues simple classification behind deep reasoning. | **`hyperframes-keyframes` + Canvas2D particles (`p5js`):** Dark slate canvas (`#080B12`); 200 color-coded request particles (cyan = simple, amber = medium, magenta = complex) jam into a single narrow funnel while a live latency bar climbs past `4,800 ms`. | `1 MODEL QUEUE` • `P95 LATENCY: 4,820 ms` | The jammed funnel rotates `90°` via GSAP `easeOutBack` and snaps into the 3-tier router node at the top of `S03`. |
| `S03` | `0:18–0:36` (`18.0s`) | **The Classifier Gate:** Introduce the lightweight intent router that scores prompt complexity in `12 ms`. | **`creative/manim-video` / SVG directed graph:** Vector DAG draws itself node-by-node (`Prompt → Feature Extractor → Complexity Score [0.0–1.0] → 3 Lanes`); cyan/amber/magenta pulses travel along bezier edges at `60 fps`. | `ROUTER GATE: +12 ms` • `TIER 1 / TIER 2 / TIER 3` | Camera zooms into the three output nodes, which expand to fill the screen as `S04`'s 3-column bento grid. |
| `S04` | `0:36–0:54` (`18.0s`) | **The Three Model Tiers:** Define what belongs in Fast Flash, Mid-Tier Workhorse, and Frontier Reasoning. | **`motion-graphics` (`bento-grid`):** Three modular dark tiles reveal sequentially with lime highlighter accents (`#A3E635`), monospace cost badges, and inline vector sparklines showing token throughput per tier. | `T1 FLASH ($0.10/1M)` • `T2 WORKHORSE ($0.80/1M)` • `T3 FRONTIER ($15.00/1M)` | The three bento tiles compress vertically into horizontal race lanes for `S05`'s live benchmark comparison. |
| `S05` | `0:54–1:12` (`18.0s`) | **Live Latency Race:** Prove end-to-end speed on a realistic 100-task workload side-by-side. | **`motion-graphics` (`charts` + `stat`) + `kallaway-glass`:** Frosted glass split-screen race: top bar (`Monolith Only`) crawls to `142s` while bottom bar (`Routed Stack`) finishes in `38s` with a glowing `-73%` hero delta badge. | `100 TASKS: MONOLITH 142s vs ROUTED 38s (-73%)` | The `-73%` badge slides left to become the Y-axis anchor of `S06`'s quality-vs-cost scatter plot. |
| `S06` | `1:12–1:30` (`18.0s`) | **The Quality Trap (Fallback Guard):** Explain why naive routing fails without confidence thresholds and escalation. | **`editorial-collage` + animated SVG chart:** Warm archive paper card sweeps over the dark grid; a vector confidence meter (`0.00–1.00`) shows a low-confidence `0.42` query automatically bouncing from Tier 1 up to Tier 3 before output. | `CONFIDENCE < 0.65 → AUTO-ESCALATE TO T3` | A red editorial cutout strip tears across the frame (`swoosh` SFX at `89.8s`), revealing the terminal diff in `S07`. |
| `S07` | `1:30–1:48` (`18.0s`) | **The Verification Loop:** Show how automated schema and test checks catch silent model regressions. | **`creative/ascii-video` / vector terminal chrome (`youtube-clean`):** Crisp vector code terminal types a 6-line routing policy JSON; green `[PASS]` badges lock onto three automated verification gates (`schema`, `citation`, `latency_cap`). | `GATE 1: SCHEMA [PASS]` • `GATE 2: CITATION [PASS]` • `GATE 3: SLA [PASS]` | The three `[PASS]` pills merge into a single golden ledger line that feeds `S08`'s 30-day production telemetry chart. |
| `S08` | `1:48–2:04` (`16.0s`) | **Real Production Numbers:** Ground the architecture in 30-day workspace spend and pass-rate data. | **`motion-graphics` (`kallaway-glass` + `charts`):** Dual-axis vector area chart draws 30 days of volume: task volume rises `3.4x` while daily spend drops `68%` and first-pass QA holds at `98.2%`. | `VOLUME +340%` • `SPEND -68%` • `QA PASS 98.2%` | The chart line flattens into a clean timeline rail that steps through `S09`'s 3-step implementation checklist. |
| `S09` | `2:04–2:18` (`14.0s`) | **How to Ship It Today:** Give the viewer three concrete rules they can implement in one afternoon. | **`motion-graphics` (`bento-grid`):** Three numbered step cards snap in with spring physics (`1. Log every prompt + cost`, `2. Route top 3 deterministic intents to T1`, `3. Add confidence fallback to T3`). | `STEP 1: LOG` • `STEP 2: SPLIT TOP 3` • `STEP 3: FALLBACK` | At `2:17.5`, the music bed cuts completely (`0.5s` crisp silence) as the three cards fold into the centre emblem of `S10`. |
| `S10` | `2:18–2:30` (`12.0s`) | **The Payoff:** Land the closing takeaway in silence, then hold the final summary frame cleanly. | **`motion-graphics` (`kallaway-glass` + `logo-reveal`):** Aurora glass hero card on `#080B12`; SVG path draws the 3-lane router emblem while the final spoken line lands in crisp silence, followed by a subtle ambient chord tail. | `STOP PAYING FRONTIER PRICES FOR ROUTINE WORK.` | Hold animated aurora glow + subtle vector pulse through `150.0s` (`0` frozen frames) and fade audio cleanly at `-14.0 LUFS`. |

---

## Pitfalls

- **Double delivery when several parties post the same render.** Ultron posts its own Stage 9 delivery; a supervising watcher that also auto-uploads the newest MP4 creates a duplicate in #content-pipeline. Before posting, check the project's `DELIVERY.json` / `renders/discord-post.json` for an existing `final_delivery` message id and only post when there is none (or the owner asked for a re-post).
- **Parking a build on owner answers with no nudge.** Stage 1/3/5 stop-and-ask gates are correct, but posting questions and going silent leaves a job stalled with zero progress — the owner sees "no video" and assumes the agent is idle. Whenever a gate hands the owner a question batch, either (a) auto-apply the stated Default Assumptions and proceed after a bounded wait, or (b) schedule an explicit nudge to the channel. Never leave an open gate with no follow-up; a silent stalled job is a fault, not a neutral state.
- **Spending full-reel render time before hook/outline/sample-scene approval.** Jumping from a one-line prompt straight to a full multi-scene render wastes compute and produces unsteerable videos. Always lock `BRIEF.md` (Stage 1), render only the Stage 4 sample scene (`scene-01-sample.mp4`), and get owner sign-off at Stage 5 before full Stage 6 rendering.
- **Downloading or re-cutting third-party videos.** Never fetch YouTube/Vimeo/social videos or build reaction cuts over third-party footage — it is permanently forbidden by owner decision (`[REDACTED_PHONE]`). Build all visuals in code.
- **Treating stock footage or stills as the video's backbone.** A slideshow of stills or stock clips is an automatic FAIL. Supporting stills/music/SFX are optional garnish; code-drawn motion graphics and diagrams carry every scene.
- **Static frames in motion scenes.** A broken GSAP selector, unstarted timeline, or CSS variable typo leaves a scene frozen while audio plays. Stage 4 and Stage 8's `freezedetect` + `vision_analyze` watch pass catches this; treat any frozen motion scene as an automatic FAIL.
- **Citing search pages in the optional asset ledger.** When optional supporting stills/music/SFX are used, `https://www.pexels.com/search/ai/` or `https://www.google.com/search?q=...` does not prove licence provenance and is rejected by `scripts/asset_ledger.py`. Always record the individual asset page URL.
- **Using `<audio data-src="...">` in HyperFrames.** HyperFrames requires `src="assets/..."` on `<audio>` and `<video>` tags; `data-src` causes `media_missing_src` errors and silent renders.
- **Reinventing existing domain skills.** Never hand-roll caption engines, beat extractors, or HyperFrames scaffolding from scratch — load the linked skill in `## Existing Skills to Reuse`.

## Verification

Prove the pipeline installation, link resolution, and helpers work offline via `terminal`:

```bash
[REDACTED_PATH] -m pytest scripts/test_asset_ledger.py scripts/test_corpus_index.py -q
```

All tests in `scripts/test_asset_ledger.py` and `scripts/test_corpus_index.py` must pass, confirming licence enforcement, corpus secret exclusion, relative link resolution from `skills/creative/ultron-video-pipeline/`, and absence of forbidden third-party download/recut language.
