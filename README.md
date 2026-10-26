# Claude Code Video Skills

A cleaned, secret-free collection of the fleet's video-generation and video-editing skills that are designed for or usable by Claude Code.

## What is included

The `skills/` directory contains 39 deduplicated skill directories covering HyperFrames, Remotion, Manim, procedural motion graphics, captions, music-driven video, explainers, product promos, PR explainers, talking-head editing, short-form editing, media operations, and supporting animation/audio workflows.

See [`inventory.json`](inventory.json) for the machine-readable inventory and [`docs/reviews/claude-video-skills-inventory-2026-10-26.md`](https://github.com/maddysjarvisv1/claude-code-video-skills/blob/main/docs/reviews/claude-video-skills-inventory-2026-10-26.md) for classification and the security review.

## Install into Claude Code

Clone the repository, then copy one or more skill directories into a Claude Code project or your user skill directory:

```bash
git clone https://github.com/maddysjarvisv1/claude-code-video-skills.git
mkdir -p .claude/skills
cp -R claude-code-video-skills/skills/hyperframes .claude/skills/
cp -R claude-code-video-skills/skills/short-form-edit .claude/skills/
```

For a user-wide install, copy to `~/.claude/skills/` instead. Keep each skill directory intact so its `references/`, `scripts/`, templates, and tests remain available.

## Runtime notes

These are workflow guides, not bundled binaries. Read each `SKILL.md` before use and install its documented dependencies (for example Node, FFmpeg, HyperFrames, Remotion, or local transcription tools) according to your environment. Do not commit credentials; provide API keys only through the runtime's supported secret store or environment.

## Provenance and cleaning

The files were collected from the local Hermes/Claude skill fleet, deduplicated by skill name, and sanitized for public publication. Local absolute paths, personal identifiers, credential-like literals, and test-only secret fixtures were redacted. Symlink targets were not copied across the public boundary.
