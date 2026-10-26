# Stage 8 (VERIFY) — Pre-Delivery Quality Gate Checklist

Nothing is delivered to Discord `#content-pipeline` (`[REDACTED_PHONE]`) until **all seven verification checks** pass and are recorded in `VERIFY-REPORT.md`.

> **AUTOMATIC FAIL RULE:** A static frame where motion was promised is an **automatic FAIL**. Never publish a render you have not watched across its motion windows.

---

## Pre-Delivery Checklist (All 7 Must Pass)

- [ ] **1. File exists at stated path with stated byte size**
  - Verify the rendered output file exists on disk, is non-empty (`size_bytes > 0`), and record both the exact absolute path and exact byte size (`stat -c "%n %s"`).
  - Never claim a render exists without stating its file path and byte count.

- [ ] **2. You WATCHED the rendered video (visual & motion inspection)**
  - Sample frames across every scene and transition (at least 1 frame per second or start/mid/end of every `EDL.json` / `STORYBOARD.md` beat) and inspect them with `vision_analyze` (or HyperFrames `npx hyperframes snapshot` / `compare`).
  - Confirm visual hierarchy, text legibility (AA contrast, zero text clipping or overlap), safe-zone compliance, and intended choreography.

- [ ] **3. No static frame where motion was promised (AUTOMATIC FAIL if violated)**
  - For every scene or beat that promises animation, kinetic typography, camera movement, or procedural diagram/chart motion in `STORYBOARD.md`, compare consecutive sampled frames (`t_start + 0.2s`, `t_mid`, `t_end - 0.2s`) using `ffmpeg` `tblend=all_mode=difference` / `ssim` or frame-hash comparison.
  - Identical consecutive frames (`SSIM == 1.0` or zero pixel delta) inside a promised motion window is an **automatic FAIL** — fix the timeline/keyframe binding and re-render before delivery.

- [ ] **4. Duration within the asked range**
  - Probe exact container duration via `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 <file.mp4>`.
  - Confirm the measured duration falls within the target window specified in `BRIEF.md` (default `±15%` of target duration, or exact bounds if specified by the owner).

- [ ] **5. Audio present, audible, and not clipped**
  - Probe audio stream presence via `ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels <file.mp4>` (unless `BRIEF.md` explicitly requested a silent/unnarrated render).
  - Measure loudness and peak level via `ffmpeg -i <file.mp4> -af astats=metadata=1:reset=0,ebur128=peak=true -f null -`:
    - Integrated loudness near target (`-14.0 LUFS ± 2.0 LUFS` for narrated pieces; never silent `<-50 LUFS`).
    - True peak / max sample level strictly below clipping (`max_volume < -0.1 dBFS`, zero clipped samples).

- [ ] **6. Captions present and in sync**
  - If burned-in captions were requested (`embedded-captions` or caption track), verify via sampled frames and `words.json` that on-screen words match spoken narration within `≤ 100ms` drift and sit inside the caption safe zone.
  - If sidecar captions (`.srt` / `.vtt`) were requested, verify the file exists, parses cleanly, has monotonic non-overlapping timestamps, and matches the spoken script through the final word.

- [ ] **7. Generative visual backbone + optional supporting assets licensed (`assets_ledger.json` verified)**
  - Confirm the video's visual backbone is built in code (never stock-footage-only or a static slideshow). Generated code visuals need no licence entry because they are ours.
  - If any optional supporting stills, music, or SFX files exist in `assets/`, run `python3 [REDACTED_PATH] verify --ledger assets_ledger.json --assets-dir assets` and confirm exit code `0` (`OK: N licensed asset(s) verified`).

---

## Canonical Verification Commands (`terminal`)

Run these checks in the project workspace and record their outputs in `VERIFY-REPORT.md`:

```bash
# 1. File path + exact byte size
stat -c "path=%n size_bytes=%s" renders/final.mp4

# 2 & 4. Stream + duration + resolution probe
ffprobe -v error -show_entries format=duration,size -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate \
  -of json renders/final.mp4

# 3. Motion check (detect frozen/static frames across motion windows; freeze > 0.5s flags an issue)
ffmpeg -v error -i renders/final.mp4 -vf "freezedetect=n=-60dB:d=0.5" -f null - 2>&1

# 5. Audio loudness & clipping check
ffmpeg -nostats -i renders/final.mp4 -af "astats=measure_perchannel=0,ebur128=peak=true" -f null - 2>&1 | grep -E "Integrated|Peak|Max level|Flat factor"

# 7. Asset licence ledger gate
python3 [REDACTED_PATH] verify --ledger assets_ledger.json --assets-dir assets
```

---

## `VERIFY-REPORT.md` Template

Write `VERIFY-REPORT.md` before entering Stage 9 (DELIVER):

```markdown
# Verification Report — <project-slug>

- **File path:** `/abs/path/to/renders/final.mp4`
- **Byte size:** `<exact bytes>`
- **Dimensions & FPS:** `<width>x<height> @ <fps> fps (<aspect>)`
- **Duration:** `<measured_sec>s` (target: `<target_sec>s`, status: PASS)
- **Watched & inspected:** Sampled `<N>` frames across all `<M>` scenes via `vision_analyze` (status: PASS)
- **Motion check:** Zero static/frozen frames in promised motion windows (`freezedetect` + frame diff: PASS)
- **Audio check:** Stream `<codec>`, integrated `<LUFS> LUFS`, peak `<dBFS> dBFS`, clipped samples `0` (status: PASS)
- **Captions check:** `<burned-in | sidecar .srt>`, sync drift `<ms>ms` against `words.json` (status: PASS)
- **Asset ledger check:** `asset_ledger.py verify` — `<K>` assets verified, 0 unlicensed/denied (status: PASS)
```
