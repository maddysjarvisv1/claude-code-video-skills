---
name: videogen-openrouter
description: "Use when generating video with OpenRouter's video API."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, generation, openrouter, api, pricing]
    category: creative
---

# Video generation via OpenRouter

OpenRouter serves **video generation** on a dedicated async endpoint — separate from the chat models,
so the normal `/api/v1/models` list does NOT show them. Use the key already in `~/.hermes/.env`
(`OPENROUTER_API_KEY`).

## When to Use

- A reel needs **generated footage** (B-roll/scene) that stock can't supply.
- A talking-head must be produced from a photo (avatar models).
- Analysing whether to pay a managed video service — usually: don't, we render locally for $0.

## Discovery

```bash
curl "https://openrouter.ai/api/v1/videos/models" -H "Authorization: Bearer $OPENROUTER_API_KEY"
```
Each model returns `supported_durations`, `supported_resolutions`, `supported_aspect_ratios`,
`supported_sizes`, `pricing_skus` and `allowed_passthrough_parameters`. **Validate `duration`,
`resolution` and `aspect_ratio` against those lists** — unsupported values return HTTP 400.

## Flow (async — video takes minutes)

1. `POST /api/v1/videos` `{model, prompt, duration, resolution, aspect_ratio, generate_audio}` →
   `{id, polling_url, status}`
2. Poll `GET /api/v1/videos/{id}` every ~30 s until `status == "completed"` (or `failed` → read `error`).
3. Download from `unsigned_urls[0]` **with the same Authorization header**.

Networks/tools that enforce Zero Data Retention will NOT route video jobs — ZDR is not eligible here.

## Verified prices (our key, 2026-10, per second of output)

| Model | Best tier | $/s |
|---|---|---|
| `alibaba/wan-2.6` | 480p t2v | **0.04** (720p 0.08, 1080p 0.12) |
| `google/veo-3.1-lite` | 720p **with audio** | **0.05** (silent 0.03) |
| `kwaivgi/kling-v3.0-std` | 720p | 0.084 (with audio 0.126) |
| `google/veo-3.1-fast` | 720p audio | 0.10 |
| `minimax/hailuo-3-max` | 480p | 0.05 |
| `x-ai/grok-imagine-video` | 480p | 0.05 |
| `google/veo-3.1` | 720p audio | 0.40 (hero shots) |
| `black-forest-labs/flux-video-edit` | edit existing video | **0.03** |
| `runway/aleph-2` | in-context video edit | 0.28 |
| `heygen/avatar-iv` | photo → lip-synced presenter | 0.05 |

## How to choose

- **B-roll for a 50 s reel**: Wan 2.6 or Veo 3.1 Lite → **~$2–2.50**. Cheapest real upgrade to a reel.
- **Editing existing footage** (captions, cards, cuts): our local HyperFrames + ffmpeg — **$0**.
  Pay for a generative *edit* model only to change content that isn't there (add/remove objects).
- **Avatar/talking head**: `heygen/avatar-iv` at $0.05/s is usually cheaper than a HeyGen subscription.
- **Do not** buy managed renderers (Shotstack/Creatomate/Plainly, $39–329/mo) — our local pipeline
  already produces that output for free.

## Pitfalls

- **Generated clips come back at 24 fps**, not 30/60. Placing them in a 30 fps timeline is fine (the
  renderer holds each source frame), but never assume frame parity when doing frame-accurate maths.
- Resolution is quantised: a `480p` 9:16 request returns **496×864**, not 480×854 — read the file, don't
  assume the pixel size from the label.
- Chat-model listing hides video models; a `/models` probe returning none does **not** mean unavailable.
- Video generation is async — never block a worker's turn waiting; poll, or run it as a background job.
- Every vendor bills successful generations even if you reject the output — cap retries.
- Re-check prices before budgeting; these vendors cut prices often.
