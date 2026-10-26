# Design system for video — the anti-slop contract

Tutorial finding that explains why AI edits look amateur: *"Never rely on an LLM's default generation
settings without strict design constraints. Default outputs result in generic 'AI vibe-coded slop'."*

So a video build MUST receive explicit tokens. Copy this file into the render workspace and fill it in
before generating anything.

## Tokens (fill per brand)

```yaml
brand: ROI Infotech
logo: public/assets/logo.svg          # SVG, never a bitmap
palette:
  bg:        '#0F172A'                 # deep slate — used behind cards
  fg:        '#FFFFFF'
  accent:    '#F59E0B'                 # highlight/emphasis (numbers, key words)
  positive:  '#22C55E'                 # checkmarks / benefits
  negative:  '#EF4444'                 # problem callouts (slow, insecure…)
  muted:     '#94A3B8'                 # secondary text — NEVER below 4.5:1 on its plate
type:
  family:    Inter                      # one family; weights 400/700 only
  headline:  72px                       # min — at 1080 width
  subhead:   54px
  caption:   54px                       # min — captions never smaller
  label:     40px                       # min — anything smaller is unreadable on a phone
spacing:
  safe_margin: 72px                     # keep all text inside this margin
  card_radius: 24px
  card_pad:    40px
caption_zone: bottom 28% of frame       # never over the speaker's face
motion:
  beat_max_s: 3.0                       # no static visual state longer than this
  ease:       'cubic-bezier(.2,.8,.2,1)'  # ease-in with a tiny overshoot, then settle
  transform_only: true                  # animate scale/translate/opacity — never left/top
audio:
  lufs: -14
  stems: [voice, music, sfx]            # separate; SFX never baked into music
  pre_roll_ms: 80                       # gap before speech so the first consonant never clips
```

## The five rules that produce the look

1. **Anchor text to a container.** No plain centred text on a gradient with floating particles — that
   *is* the cheap look. Put type on a card, a glass panel, or a UI surface.
2. **One idea per beat**, and a new beat every 1.5–3 s, keyed to the words actually being spoken.
3. **Show, don't caption** — a number becomes a counter, a comparison a split, a process a step graphic.
4. **Vector only.** Author SVG/HTML; never scale a bitmap.
5. **Restraint.** No emoji, no effect-per-second, no unrelated B-roll.

## Contrast

Every text element must pass **WCAG AA** against what is actually behind it — add a scrim/plate if
needed. A ghosted line is worse than no line.
