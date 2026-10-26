# Stage 4 (GENERATE VISUALS) — Optional Supporting-Asset Licence Protocol

Ultron generates its primary visuals in code (motion graphics, animated diagrams, data visualisation, kinetic typography, transitions, shapes, particles). **Generated visuals need no licence record because they are ours.**

Licensed stills, music, and SFX are strictly **OPTIONAL supporting assets** (never load-bearing — a video that is only stock footage or a slideshow of stills is not acceptable). Whenever any optional third-party still, icon, font, music track, or sound effect is placed in `<project>/assets/`, it MUST be recorded in `assets_ledger.json` via `scripts/asset_ledger.py`.

> **Hard Limit:** Never download, rip, or re-cut a third-party video (no YouTube/Vimeo/social video fetch, no reaction edits). Third-party video download is permanently out of scope by owner decision (`[REDACTED_PHONE]`).

## Hard Rules for Optional Supporting Assets

1. **No unlicensed assets (FAIL-CLOSED).** Any file in `assets/` missing from `assets_ledger.json`, lacking a `licence` field, shorter than 3 characters, or containing only punctuation is a hard fail (`AssetLicenceError`).
2. **Positive allow-list enforcement.** `scripts/asset_ledger.py` is fail-closed: an asset is accepted ONLY if its normalized licence matches a recognized family on the positive allow-list (`CC0`, `CC-BY`, `CC-BY-SA`, `CC-BY-NC` [accepted with an explicit non-commercial flag/warning], `Public Domain`, `MIT`, `Apache-2.0`, `BSD`, `OFL`, `Pixabay`, `Pexels`, `Unsplash`, `Generated-Local`, `Owner-Supplied`, or `used with written permission — <Granter Name>`). Any unrecognised string is refused.
3. **Phrase-based deny-list fast path.** `scripts/asset_ledger.py` also immediately refuses any licence containing denied phrases (case-insensitive, `licence`/`license` normalized):
   - `all rights reserved`
   - `no licence stated` / `no license stated` / `no licence` / `no license`
   - `unknown` / `unclear` / `none` / `see website`
   - `unlicensed` / `unlicenced` / `not licensed`
   - `proprietary` / `copyright` / `copyrighted`
   - `N/A` / `TBD` / `TODO` / `unverified`
   - Note: AIS brand assets inside `[REDACTED_PATH]` are **not** licensed for reuse and must never be shipped.
4. **Provenance-first URLs.** `source_url` MUST point to the exact canonical page where the asset and its licence are published (e.g. `https://commons.wikimedia.org/wiki/File:...`, `https://unsplash.com/photos/...`, or `local://procedural/sfx.py` for locally generated audio).
   - **Never cite a search-results page** (`/search?q=...`, `/s/photos/...`, `/images/search/...`, Google/Bing image search URLs). `scripts/asset_ledger.py` automatically rejects search-results URLs.

---

## Required Fields per Optional Supporting Asset

| Field | Requirement | Example |
|---|---|---|
| `local_path` | Project-relative path to the frozen local file | `assets/diagram_reference.svg` |
| `source_url` | Exact asset page URL (or `local://<generator>` for procedural/TTS audio) | `https://commons.wikimedia.org/wiki/File:Transformer_architecture.svg` |
| `licence` | SPDX identifier or canonical permissive licence name | `CC-BY-4.0`, `CC0-1.0`, `CC-BY-SA-4.0`, `Pexels`, `Pixabay`, `Unsplash`, `MIT`, `Generated-Local`, `Owner-Supplied` |
| `author` | Creator name, organization, or local generator | `Wikimedia Contributor` |
| `used_in` | Scene ID and/or timestamp window where the supporting asset appears | `scene-02 (00:08-00:14)` |

---

## Optional Supporting-Asset Workflow

1. **Build visuals in code first:** Use `hyperframes`, `motion-graphics`, `manim-video`, `p5js`, `animate`, or `remotion-video` for the visual backbone. Reach for optional supporting assets only for music beds, SFX, or a specific licensed reference still.
2. **Prefer free/open repositories with clear per-asset licence pages:**
   - Wikimedia Commons (`CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `Public Domain`)
   - Pixabay / Unsplash / Pexels (record the exact item page URL and author)
   - Locally synthesized audio (`licence: "Generated-Local"`, `source_url: "local://kokoro-tts"` or `"local://sfx.py"`)
   - Owner-provided files (`licence: "Owner-Supplied"`, `source_url: "file://[REDACTED_PATH]"`, `author: "Owner"`)
3. **Record each optional supporting asset immediately:**
   ```bash
   python3 [REDACTED_PATH] add \
     --ledger assets_ledger.json \
     --local-path "assets/diagram_reference.svg" \
     --source-url "https://commons.wikimedia.org/wiki/File:Transformer_architecture.svg" \
     --licence "CC-BY-SA-4.0" \
     --author "Wikimedia Contributor" \
     --used-in "scene-02 (00:08-00:14)"
   ```
4. **Verify any supporting assets before Stage 6 (BUILD) and Stage 8 (VERIFY):**
   ```bash
   python3 [REDACTED_PATH] verify \
     --ledger assets_ledger.json \
     --assets-dir assets
   ```
   A non-zero exit code (`REFUSED: ...`) blocks rendering and delivery until the offending asset is replaced or removed.
5. **Export attribution table for Stage 9 (DELIVER):**
   ```bash
   python3 [REDACTED_PATH] list --ledger assets_ledger.json
   ```
