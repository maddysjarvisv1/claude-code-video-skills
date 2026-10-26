# Stage 1 (CLARIFY) — Intake Question Set

Use this reference during **Stage 1 (CLARIFY)** whenever the brief leaves any output-changing parameter unspecified.

## Rules

- **Batch into ONE list.** Never drip-feed questions across multiple turns.
- **Never ask more than 7 questions.** Omit any question the owner's brief already answered.
- **Generative graphics by default.** Never ask for a third-party video to download, rip, or re-cut, and never ask about a reaction layout — Ultron generates all visuals in code.
- **Usable verbatim.** Copy the question block below directly, trimming only already-answered items.
- **"You decide" rule:** If the owner says *"you decide"*, *"up to you"*, or *"just run with defaults"*, stop asking immediately, lock the **Default Assumptions** table below into `BRIEF.md`, and state those assumptions explicitly in the Stage 3/5 approval gate and Stage 9 delivery note.

---

## Verbatim Question Block (<= 7 Questions)

```markdown
Before I lock the brief and write the hook + outline, please confirm (or reply **"you decide"** for defaults):

1. **Length & deadline:** What target duration (e.g. 30–45s short, 60–90s explainer, 2–3 min deep dive) and deadline should I hit?
2. **Platform & aspect ratio:** Where will this run — `9:16` vertical (Reels/Shorts), `16:9` horizontal (YouTube/web), or `1:1` / `4:5` feed?
3. **Audience:** Who is the viewer (technical builders, execs, general audience) and what prior context can I assume?
4. **Tone:** What spoken and visual register fits best (plain analytical, punchy/contrarian, warm storytelling)?
5. **Research sources:** Should I use my own primary-source web + workspace corpus research, stick strictly to URLs/PDFs/notes you provide, or combine both?
6. **Voiceover & audio:** Do you want a spoken voiceover (with word-locked code animations and a ducked music/SFX bed) or an unnarrated motion-first piece?
7. **Caption style & generative visual theme:** Do you want burned-in kinetic captions (`embedded-captions`), sidecar `.srt`/`.vtt`, or no captions — and any preferred generative style (`kallaway-glass`, `editorial-collage`, `bento-grid`, `neo-brutal`, `youtube-clean`) or brand palette?
```

---

## Dimension-to-Artifact Mapping

Every question above maps directly to a field in `BRIEF.md`:

| # | Dimension Covered | `BRIEF.md` Field | Why It Changes the Output |
|---|---|---|---|
| 1 | Length + deadline | `target_duration_sec`, `deadline` | Sets spoken word budget (~2.5 words/sec), scene count, and build vs Ag2 dispatch ceiling. |
| 2 | Platform / aspect | `platform`, `aspect_ratio`, `resolution` | Sets root canvas dimensions (`1080x1920`, `1920x1080`, `1080x1080`) and caption safe zones. |
| 3 | Audience | `audience` | Controls terminology grounding (`writing-beats`) and diagram abstraction depth. |
| 4 | Tone | `tone` | Controls spoken rhythm (`humanizer`), pacing, and motion-graphics energy. |
| 5 | Own research vs owner's sources | `research_mode`, `owner_sources` | Determines whether Stage 2 mines only owner PDFs/notes or adds primary web + corpus citations. |
| 6 | Voiceover | `voiceover`, `audio_bed` | Switches between Level 3 local TTS + `faster-whisper` word-locked `EDL.json` vs beat-grid / unnarrated timing. |
| 7 | Caption style + visual theme | `caption_style`, `style_slug`, `brand_tokens` | Selects burned-in `embedded-captions` track vs `.srt` sidecar and locks the code-drawn style palette before Stage 4. |

---

## "You Decide" Default Assumptions

When the owner delegates choices (*"you decide"*), write these defaults into `BRIEF.md` under `## Stated Assumptions` and echo them in the delivery summary:

| Dimension | Default Assumption |
|---|---|
| **Length** | `150s` (`2–3 min` deep-dive explainer, ~360–400 spoken words across 8–12 scenes) or `45s` (`35–55s`) for short-form reels |
| **Platform / Aspect** | `16:9` horizontal (`1920x1080`, 30 fps) for topic explainers or `9:16` vertical (`1080x1920`, 30 fps) for short-form |
| **Audience** | Technical-adjacent general audience — ground specialist terms on first use |
| **Tone** | Warm, confident, plain spoken English; zero hype or AI clichés |
| **Research Sources** | Workspace corpus (`scripts/corpus_index.py`) first, supplemented by verified primary web sources |
| **Deadline** | Same-session turnaround (single pass after hook + outline + sample scene approval) |
| **Voiceover** | Yes — local TTS voiceover normalized to `-14 LUFS` with word-level `words.json` timestamps |
| **Caption Style** | Burned-in quiet `anchor` rail captions synced to `words.json` + `.srt` sidecar |
| **Generative Visual Theme** | Code-drawn `kallaway-glass` / `bento-grid` dark slate canvas (`#080B12` background, `#F8FAFC` vector text, `#38BDF8` accent, AA contrast verified) |
