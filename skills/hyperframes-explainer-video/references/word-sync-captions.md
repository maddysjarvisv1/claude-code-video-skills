# Word-synced narration video

Turn a TTS voiceover into a video whose captions, kinetic supers, and chips land on the exact spoken word — no hand-keyframing.

## Pipeline

1. Write the narration script first (facts are the agent's job, not the user's). TTS it with `text_to_speech` → mp3.
2. Transcribe locally for word timings `[{w, s, e}, ...]` (model `base.en`, cpu, int8). Reusable skeleton lives under `[REDACTED_PATH]` (`word_times.py` emits `words.json`; `build_video.py` emits the composition).
3. GENERATE `index.html` from `words.json`; never hand-keyframe when timings exist:
   - Captions = 2–3 word / ≤20-char chunks; each chunk is its own `.clip cap` element. `data-start`/`data-duration` drive show/hide (framework-owned) — animate only the INNER span for the fade (tweening the `.clip` with visibility/autoAlpha trips `gsap_animates_clip_element`).
   - A super / card / chip lands on the beat that NAMES it: look up that word's `start` time, don't guess.
   - **Code-drawn physical actions also bind to `words.json` (Level 3 choreography):** Even when narration is synthesized locally from known text (Kokoro ONNX or Edge TTS), always run `faster-whisper` back on the generated audio so `words.json` records the exact second of every word, and bind diegetic canvas/SVG drawing actions (`action_cues`: a blade strike, an oblique explosion, a water drop, a stamp slam) to the trigger word's exact `s` timestamp ("When the voice says, 'He struck,' the blade moves on struck, not near it, on it"). *Why:* line-level TTS durations only tell you when a sentence starts and ends, leaving intra-scene drawing actions guessing the beat.
   - Keep timed windows NON-overlapping per canvas zone (supers mid-band, cards top, chips one row, captions bottom). `content_overlap` lint fires on two text blocks overlapping in TIME at the same zone → trim the durations / give each its own zone; don't paper over with layout-overlap flags.
   - Place supers/captions BELOW a presenter's face (face upper third; clear bottom band for type) with a gradient scrim so supers stay legible without occluding the subject.
4. Free presenter footage: Pexels / Pixabay / Mixkit. SELECT with vision, not just metadata: presenter facing camera, face in the upper third, calm background, and **silent** (no music/talk — your TTS narration is the only audio); pick a vertical clip for a 9:16 canvas. Record the source id/link in a `CREDITS.txt`.
5. `npx hyperframes check` must pass (0 errors, contrast WCAG AA, layout clean) BEFORE render. After render, verify BOTH tracks:
   - audio real: ffprobe stream + volumedetect (present, non-silent, duration matches) — `scripts/verify_render.sh`;
   - visuals real: extract frames (`ffmpeg -ss T -i out.mp4 -frames:v 1 f.jpg`) across the timeline, stitch a contact sheet (`xstack` grid), and eyeball it with vision for collisions/legibility. A passing check does not prove the frames look right.

## Pitfall: faster-whisper → PyAV kwarg shim

faster-whisper 1.2.1 calls `av.open(metadata_errors=...)` unconditionally; the PyAV 19.0.1 wheel for Python 3.14 rejects that kwarg, so the transcribe step fails at import/load. Fix (this is the FIX, not a dead-end — the pipeline works once it is in place), wrap `av.open` BEFORE importing faster_whisper:

```python
import functools, av
_orig = av.open
@functools.wraps(_orig)
def _open(*a, **kw):
    kw.pop("metadata_errors", None)
    return _orig(*a, **kw)
av.open = _open
from faster_whisper import WhisperModel
```

## Cost

Word-syncing needs NO paid model: edge TTS + local Whisper + the composition generator are all free; the only cost is execution tokens. The frontier model is the video's SUBJECT, never its generator.