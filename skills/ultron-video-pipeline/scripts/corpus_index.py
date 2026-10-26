#!/usr/bin/env python3
"""Workspace corpus index for the Ultron (`vid`) video pipeline.

Indexes Ultron's authorized read-corpus into a local SQLite FTS5 index:
  - [REDACTED_PATH]
  - [REDACTED_PATH]
  - [REDACTED_PATH]
  - [REDACTED_PATH]
  - [REDACTED_PATH]

Safety rules:
  - Never index .env files, token/credential/secret/key files, or any file matching secret patterns.
  - Reports indexed document counts per root.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

DEFAULT_ROOTS: tuple[str, ...] = (
    "[REDACTED_PATH]",
    "[REDACTED_PATH]",
    "[REDACTED_PATH]",
    "[REDACTED_PATH]",
    "[REDACTED_PATH]",
)

DEFAULT_DB_PATH = os.environ.get(
    "ULTRON_CORPUS_DB",
    os.path.join(tempfile.gettempdir(), "ultron_corpus_index.db"),
)

INDEXABLE_EXTENSIONS = {
    ".md",
    ".txt",
    ".html",
    ".csv",
    ".json",
    ".yaml",
    ".yml",
    ".pdf",
}

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "site-packages",
    "secrets",
    "browser-session",
    "cache",
    "logs",
    ".locks",
    "graphify-out",
}

SECRET_FILENAME_RE = re.compile(
    r"(^|/)\.(?:env|env\..+|netrc|npmrc|pypirc)$"
    r"|(?:\.env$|\.pem$|\.key$|\.p12$|\.pfx$|\.keystore$)"
    r"|(?:^|/)(?:auth\.json|credentials\.json|client_secret.*\.json|id_rsa[^/]*|id_ed25519[^/]*|id_ecdsa[^/]*|id_dsa[^/]*)$"
    r"|(?:^|/)[^/]*(?:token|secret|credential|password|passwd|apikey|api_key|api-key)[^/]*$",
    re.IGNORECASE,
)

SECRET_CONTENT_PATTERNS = (
    # OpenAI / OpenRouter / Anthropic keys
    re.compile(r"\bsk-(?:proj-|or-v1-|ant-[A-Za-z0-9_-]+-)?[A-Za-z0-9_-]{20,}"),
    # Discord bot tokens: base64 user id + . + base64 timestamp + . + base64url HMAC (typically 27-38 chars)
    re.compile(r"\b[A-Za-z0-9_-]{16,36}\.[A-Za-z0-9_-]{6,10}\.[A-Za-z0-9_-]{24,45}\b"),
    # Discord webhook URLs
    re.compile(
        r"https?://(?:ptb\.|canary\.)?discord(?:app)?\.com/api(?:/v\d+)?/webhooks/\d+/[A-Za-z0-9_-]+",
        re.IGNORECASE,
    ),
    # GitHub tokens (ghp_, gho_, ghu_, ghs_, ghr_, github_pat_)
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    # AWS access key IDs and aws_secret assignments
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\baws_secret[a-z0-9_]*\s*[:=]\s*['\"]?[A-Za-z0-9/+_=.-]{8,}"),
    # Slack tokens (xoxb-, xoxp-, xoxa-, xoxr-, xoxs-, xoxe-)
    re.compile(r"\bxox[bpaers]-[A-Za-z0-9-]{10,}\b"),
    # Stripe live keys (sk_live_, rk_live_)
    re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{10,}\b"),
    # SendGrid API keys (SG.)
    re.compile(r"\bSG\.[A-Za-z0-9_.-]{20,}\b"),
    # Google API keys (AIza + 35 chars) and OAuth access tokens (ya29.)
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    re.compile(r"\bya29\.[A-Za-z0-9_-]{20,}\b"),
    # Generic Bearer tokens (Bearer [REDACTED] by 20+ token characters)
    re.compile(r"\bBearer\s+[A-Za-z0-9_\-./+=]{20,}"),
    # Private key blocks
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP |DSA |)?PRIVATE KEY-----"),
    # JWTs
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\b"),
    # Secret-ish env/config assignments
    re.compile(
        r"(?m)^\s*(?:export\s+)?[A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE_KEY)[A-Z0-9_]*\s*=\s*['\"]?[A-Za-z0-9_\-./+=]{8,}"
    ),
)

FENCED_BLOCK_RE = re.compile(
    r"(?ms)^[ \t]*(`{3,}|~{3,})[^\n]*\n(.*?)^[ \t]*\1[ \t]*$"
)

PLACEHOLDER_MARKER_RE = re.compile(
    r"(?:YOUR_[A-Za-z0-9_]*HERE"
    r"|YOUR_[A-Za-z0-9_]*(?:KEY|TOKEN|SECRET)"
    r"|<[A-Za-z0-9_-]*(?:token|key|secret|password)[A-Za-z0-9_-]*>"
    r"|x{3,}"
    r"|placeholder"
    r"|replace_me"
    r"|insert_[A-Za-z0-9_]*here"
    r"|example_(?:key|token)"
    r"|dummy_(?:key|token))",
    re.IGNORECASE,
)

HIGH_ENTROPY_TOKEN_RE = re.compile(r"\b[A-Za-z0-9_-]{32,}\b")


class CorpusCounts(dict[str, int]):
    """Dict mapping root -> indexed count, plus .withheld / .excluded metadata."""

    def __init__(
        self,
        counts: dict[str, int] | None = None,
        withheld_by_root: dict[str, int] | None = None,
    ) -> None:
        super().__init__(counts or {})
        self.withheld_by_root: dict[str, int] = dict(withheld_by_root or {})
        self.excluded_by_root: dict[str, int] = self.withheld_by_root
        self.withheld: int = sum(self.withheld_by_root.values())
        self.excluded: int = self.withheld
        self.skipped_secrets: int = self.withheld


def is_secret_path(path: str | Path) -> bool:
    norm = str(path).replace("\\", "/")
    parts = [p for p in norm.split("/") if p]
    for part in parts[:-1]:
        if part.lower() in ("secrets", "browser-session", ".ssh", ".gnupg"):
            return True
    fname = parts[-1] if parts else norm
    if fname.startswith(".env") or fname.endswith(".env"):
        return True
    if SECRET_FILENAME_RE.search(norm):
        return True
    return False


FENCED_TOKEN_RE = re.compile(r"[A-Za-z0-9_<>/+=.-]+")


def _scrub_fenced_placeholders(text: str) -> str:
    """Replace placeholder tokens inside fenced code blocks without masking adjacent secrets."""

    def _replace_token(tok_match: re.Match[str]) -> str:
        tok = tok_match.group(0)
        if PLACEHOLDER_MARKER_RE.search(tok):
            return "_"
        return tok

    def _replace_fence(match: re.Match[str]) -> str:
        fence = match.group(1)
        body = match.group(2)
        scrubbed_body = FENCED_TOKEN_RE.sub(_replace_token, body)
        return f"{fence}\n{scrubbed_body}\n{fence}"

    return FENCED_BLOCK_RE.sub(_replace_fence, text)


def _is_mixed_high_entropy_token(token: [REDACTED] -> bool:
    if len(token) < 32:
        return False
    has_upper = any(ch.isupper() for ch in token)
    has_lower = any(ch.islower() for ch in token)
    has_digit = any(ch.isdigit() for ch in token)
    return has_upper and has_lower and has_digit


def has_secret_content(text: str) -> bool:
    if not text:
        return False
    scrubbed = _scrub_fenced_placeholders(text)
    for pat in SECRET_CONTENT_PATTERNS:
        if pat.search(scrubbed):
            return True
    for match in HIGH_ENTROPY_TOKEN_RE.finditer(scrubbed):
        tok = match.group(0)
        if _is_mixed_high_entropy_token(tok):
            return True
    return False


def _read_document_text(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(str(path))
            pages = [page.get_text("text") for page in doc]
            doc.close()
            return "\n".join(pages)
        except Exception:
            try:
                from pypdf import PdfReader

                reader = PdfReader(str(path))
                return "\n".join((p.extract_text() or "") for p in reader.pages)
            except Exception:
                return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _extract_title(path: Path, body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or path.stem
    return path.stem


def _fts_query(raw_query: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9_]+", str(raw_query or ""))
    if not tokens:
        return ""
    return " ".join(f'"{tok}"' for tok in tokens)


def build_index(
    db_path: str | Path = DEFAULT_DB_PATH,
    roots: Sequence[str | Path] = DEFAULT_ROOTS,
) -> CorpusCounts:
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    try:
        conn.execute("DROP TABLE IF EXISTS corpus_fts")
        conn.execute("DROP TABLE IF EXISTS corpus_root_counts")
        conn.execute(
            "CREATE VIRTUAL TABLE corpus_fts USING fts5(path UNINDEXED, root UNINDEXED, title, body)"
        )
        conn.execute(
            "CREATE TABLE corpus_root_counts ("
            "root TEXT PRIMARY KEY, "
            "doc_count INTEGER NOT NULL, "
            "withheld_count INTEGER NOT NULL DEFAULT 0"
            ")"
        )

        counts: dict[str, int] = {}
        withheld_by_root: dict[str, int] = {}
        seen_realpaths: set[tuple[str, str]] = set()

        for root in roots:
            root_str = str(root)
            root_path = Path(root)
            count = 0
            withheld = 0
            if root_path.is_dir():
                for dirpath, dirnames, filenames in os.walk(root_path, followlinks=True):
                    kept_dirs: list[str] = []
                    for d in sorted(dirnames):
                        if d in SKIP_DIRS:
                            continue
                        if is_secret_path(Path(dirpath) / d):
                            withheld += 1
                            continue
                        kept_dirs.append(d)
                    dirnames[:] = kept_dirs

                    for fname in sorted(filenames):
                        fpath = Path(dirpath) / fname
                        if is_secret_path(fpath):
                            withheld += 1
                            continue
                        if fpath.suffix.lower() not in INDEXABLE_EXTENSIONS:
                            continue
                        try:
                            real_key = (root_str, str(fpath.resolve()))
                        except OSError:
                            continue
                        if real_key in seen_realpaths:
                            continue
                        body = _read_document_text(fpath)
                        if body is None:
                            continue
                        if has_secret_content(body):
                            withheld += 1
                            continue
                        seen_realpaths.add(real_key)
                        title = _extract_title(fpath, body)
                        conn.execute(
                            "INSERT INTO corpus_fts (path, root, title, body) VALUES (?, ?, ?, ?)",
                            (str(fpath), root_str, title, body),
                        )
                        count += 1
            counts[root_str] = count
            withheld_by_root[root_str] = withheld
            conn.execute(
                "INSERT INTO corpus_root_counts (root, doc_count, withheld_count) VALUES (?, ?, ?)",
                (root_str, count, withheld),
            )
        conn.commit()
        result = CorpusCounts(counts=counts, withheld_by_root=withheld_by_root)
        if result.withheld > 0:
            print(
                f"[corpus_index] Withheld {result.withheld} secret-matching file(s) from indexing.",
                file=sys.stderr,
            )
        return result
    finally:
        conn.close()


def get_root_counts(db_path: str | Path = DEFAULT_DB_PATH) -> CorpusCounts:
    db_file = Path(db_path)
    if not db_file.exists():
        return CorpusCounts()
    conn = sqlite3.connect(str(db_file))
    try:
        rows = conn.execute(
            "SELECT root, doc_count, withheld_count FROM corpus_root_counts ORDER BY rowid"
        ).fetchall()
        counts = {str(r[0]): int(r[1]) for r in rows}
        withheld_by_root = {str(r[0]): int(r[2]) for r in rows}
        return CorpusCounts(counts=counts, withheld_by_root=withheld_by_root)
    except sqlite3.OperationalError:
        return CorpusCounts()
    finally:
        conn.close()


def search_index(
    db_path: str | Path,
    query: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    db_file = Path(db_path)
    if not db_file.exists():
        return []
    fts_q = _fts_query(query)
    if not fts_q:
        return []
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT path, root, title,
                   snippet(corpus_fts, 3, '[', ']', '...', 16) AS snippet,
                   bm25(corpus_fts) AS rank
            FROM corpus_fts
            WHERE corpus_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_q, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Index and search Ultron's workspace corpus."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Build or refresh the SQLite FTS corpus index.")
    p_build.add_argument("--db", default=DEFAULT_DB_PATH, help="SQLite index file path.")
    p_build.add_argument(
        "--root",
        action="append",
        dest="roots",
        default=None,
        help="Corpus root directory (repeatable; defaults to Ultron's 5 corpus roots).",
    )
    p_build.add_argument("--json", action="store_true", help="Output JSON.")

    p_search = sub.add_parser("search", help="Full-text search across the indexed corpus.")
    p_search.add_argument("query", help="Full-text query string.")
    p_search.add_argument("--db", default=DEFAULT_DB_PATH, help="SQLite index file path.")
    p_search.add_argument(
        "--root",
        action="append",
        dest="roots",
        default=None,
        help="Corpus root directory if building on demand.",
    )
    p_search.add_argument("--limit", type=int, default=20, help="Max results to return.")
    p_search.add_argument("--json", action="store_true", help="Output JSON.")

    p_stats = sub.add_parser("stats", help="Report indexed document counts per root.")
    p_stats.add_argument("--db", default=DEFAULT_DB_PATH, help="SQLite index file path.")
    p_stats.add_argument("--json", action="store_true", help="Output JSON.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build":
        roots = args.roots if args.roots else DEFAULT_ROOTS
        counts = build_index(db_path=args.db, roots=roots)
        if args.json:
            print(
                json.dumps(
                    {
                        "db": str(args.db),
                        "counts": dict(counts),
                        "withheld": counts.withheld,
                        "excluded": counts.excluded,
                        "withheld_by_root": counts.withheld_by_root,
                    },
                    indent=2,
                )
            )
        else:
            for root_str, count in counts.items():
                w = counts.withheld_by_root.get(root_str, 0)
                print(f"{root_str}: {count} file(s) indexed, {w} withheld")
            print(f"Total withheld (secret rules): {counts.withheld}")
        return 0

    if args.command == "search":
        db_file = Path(args.db)
        if not db_file.exists():
            roots = args.roots if args.roots else DEFAULT_ROOTS
            build_index(db_path=db_file, roots=roots)
        counts = get_root_counts(db_file)
        results = search_index(db_path=db_file, query=args.query, limit=args.limit)
        if args.json:
            print(
                json.dumps(
                    {
                        "query": args.query,
                        "counts": dict(counts),
                        "withheld": counts.withheld,
                        "excluded": counts.excluded,
                        "withheld_by_root": counts.withheld_by_root,
                        "results": results,
                    },
                    indent=2,
                )
            )
        else:
            for root_str, count in counts.items():
                w = counts.withheld_by_root.get(root_str, 0)
                print(f"[root] {root_str}: {count} indexed ({w} withheld)")
            for hit in results:
                print(f"{hit['path']} ({hit['title']}): {hit['snippet']}")
        return 0

    if args.command == "stats":
        counts = get_root_counts(args.db)
        if args.json:
            print(
                json.dumps(
                    {
                        "counts": dict(counts),
                        "withheld": counts.withheld,
                        "excluded": counts.excluded,
                        "withheld_by_root": counts.withheld_by_root,
                    },
                    indent=2,
                )
            )
        else:
            for root_str, count in counts.items():
                w = counts.withheld_by_root.get(root_str, 0)
                print(f"{root_str}: {count} file(s) indexed, {w} withheld")
            print(f"Total withheld (secret rules): {counts.withheld}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

