# Stage 2 (RESEARCH) — Workspace Corpus & Indexing Protocol

Ultron starts every research pass by querying the local workspace corpus before running external web searches. Do not start from nothing when the workspace already holds verified reports, notes, PDFs, or reusable visual templates.

## Authorized Corpus Roots

`scripts/corpus_index.py` indexes these five canonical roots by default (`DEFAULT_ROOTS`):

| Root | Contents | Primary Use in Video Pipeline |
|---|---|---|
| `[REDACTED_PATH]` | Durable notes, system specs, lessons, decisions, handoffs, `Video/` playbooks | Grounding facts, architectural decisions, past video lessons |
| `[REDACTED_PATH]` | Structured HTML/visual research reports | Deep-dive technical claims, visual layout inspiration |
| `[REDACTED_PATH]` | Dated ecosystem radar digests and technical reviews | Latest AI trends, model releases, benchmark numbers |
| `[REDACTED_PATH]` | Strategy reports, video digest playbooks, backtest analyses | Domain data, narrative framing, comparative tables |
| `[REDACTED_PATH]` | Installed Hermes skill library (creative, video, media, writing, PDF) | Selecting animation engines, style specs, and helper scripts |

### Additional Read-Only Reference Trees

- `[REDACTED_PATH]` and `[REDACTED_PATH]` — working video repositories and past renders.
- Existing PDFs (either inside the corpus roots or supplied by the owner) — indexed automatically by `scripts/corpus_index.py` and inspectable page-by-page using `[REDACTED_PATH]` (`pdf_read.py`, `extract_pymupdf.py`, `pdf_page_image.py`).
- Existing transcripts you own — structure scripts and pacing via `[REDACTED_PATH]` (`youtube-content`). Never download, rip, or re-cut third-party videos.

---

## Secret-Exclusion Rules (Hard Boundary)

Ultron has **zero credential access** and must never read or index secrets:

1. **Excluded filenames and directories:**
   - `.env`, `.env.*`, `*.env`, `.netrc`, `.npmrc`, `.pypirc`
   - Any file whose name matches `*token*`, `*secret*`, `*credential*`, `*password*`, `*passwd*`, `*apikey*`, `*api_key*`, `*api-key*`, or `auth.json` (regardless of extension)
   - Private keys (`*.pem`, `*.key`, `id_rsa*`, `id_ed25519*`, `id_ecdsa*`, `id_dsa*`, `*.p12`, `*.pfx`, `*.keystore`)
   - Directories: `secrets/`, `browser-session/`, `.ssh/`, `.gnupg/`, `.git/`, `node_modules/`, `.venv/`, `cache/`, `logs/`
2. **Excluded content patterns & high-entropy fallback:**
   - Any file containing Discord bot tokens (`MTIz...` 3-part base64url) or Discord webhook URLs, GitHub tokens (`ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`, `github_pat_`), AWS access keys (`AKIA...`, `ASIA...`) or `aws_secret` assignments, Slack tokens (`xoxb-`, `xoxp-`, `xoxa-`), Stripe keys (`sk_live_`, `rk_live_`), SendGrid keys (`SG.`), Google API keys (`AIza...`), OpenAI/Anthropic/OpenRouter keys (`sk-...`, `sk-or-v1-...`), generic `Bearer <20+ chars>`, JWTs, `-----BEGIN ... PRIVATE KEY-----`, or `SECRET=[REDACTED] / `API_KEY=[REDACTED] assignments is automatically withheld.
   - Any 32+ character high-entropy token mixing uppercase, lowercase, and digits is withheld unless it is inside a fenced code block and clearly marked as a placeholder (`YOUR_KEY_HERE`, `<token>`, `xxx`).
   - Every withheld file is counted and reported (`withheld` / `withheld_by_root`) so a human can see what was withheld.

---

## CLI Usage (`scripts/corpus_index.py`)

Run through `terminal`:

### 1. Build or Refresh the Index (Reports Counts per Root)

```bash
python3 [REDACTED_PATH] build --json
```

 Output reports exact indexed file counts for each of the 5 roots:
```json
{
  "db": "/tmp/ultron_corpus_index.db",
  "counts": {
    "[REDACTED_PATH]": 226,
    "[REDACTED_PATH]": 1,
    "[REDACTED_PATH]": 18,
    "[REDACTED_PATH]": 5,
    "[REDACTED_PATH]": 512
  }
}
```

### 2. Full-Text Search Across the Corpus

```bash
python3 [REDACTED_PATH] search "latest AI trends" --limit 10 --json
```

### 3. Inspect Root Counts Only

```bash
python3 [REDACTED_PATH] stats
```

---

## Stage 2 Research Artefact (`RESEARCH.md`)

Every Stage 2 run writes `RESEARCH.md` in the project directory containing:
1. **Corpus hits:** exact local file paths (`file:///...`) and quotes/data extracted from the workspace corpus (and any owner PDFs read via `productivity/pdf`).
2. **Primary web citations:** exact URLs, publication dates, and verified claims from `web_search` / `web_extract`.
3. **Claim-to-source table:** every number, benchmark, or factual statement that will appear in the script mapped to its source path or URL. Unsourced claims are cut before Stage 3.
