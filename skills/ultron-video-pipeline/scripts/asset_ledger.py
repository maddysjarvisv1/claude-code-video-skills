#!/usr/bin/env python3
"""Asset licence ledger for the Ultron video pipeline.

Records per-asset provenance:
  - local_path
  - source_url (exact asset page URL, never a search-results URL)
  - licence (SPDX identifier or canonical licence name)
  - author
  - used_in (scene / timestamp range where the asset is used)

Refuses any asset without a licence record, any licence on the deny-list
(e.g. "all rights reserved", "unknown", "proprietary", "unlicensed"),
and any search-results URL.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


class AssetLicenceError(ValueError):
    """Raised when an asset entry is missing a licence, uses a denied licence, or violates provenance rules."""


DENY_LICENCES = {
    "all rights reserved",
    "all-rights-reserved",
    "unknown",
    "unlicensed",
    "unlicenced",
    "none",
    "no licence",
    "no license",
    "no-licence",
    "no-license",
    "no licence stated",
    "no license stated",
    "unclear",
    "see website",
    "proprietary",
    "copyright",
    "copyrighted",
    "n/a",
    "na",
    "tbd",
    "todo",
    "unverified",
}

DENY_PHRASES = (
    "all rights reserved",
    "no license stated",
    "no license",
    "not licensed",
    "unlicensed",
    "unknown",
    "none",
    "unclear",
    "proprietary",
    "see website",
    "copyrighted",
    "copyright",
    "unverified",
    "n/a",
    "tbd",
    "todo",
)

ALLOW_LICENCE_FAMILIES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("CC0", re.compile(r"^(?:cc0(?:[\s-]*1\.0)?(?:\s+universal)?|creative\s+commons\s+zero(?:\s+1\.0)?)$")),
    ("CC-BY", re.compile(r"^(?:cc[\s-]+by(?:[\s-]+[1-4]\.\d)?(?:\s+international)?|creative\s+commons\s+attribution(?:\s+[1-4]\.\d)?)$")),
    ("CC-BY-SA", re.compile(r"^(?:cc[\s-]+by[\s-]+sa(?:[\s-]+[1-4]\.\d)?(?:\s+international)?|creative\s+commons\s+attribution[\s-]+sharealike(?:\s+[1-4]\.\d)?)$")),
    ("CC-BY-NC", re.compile(r"^(?:cc[\s-]+by[\s-]+nc(?:[\s-]+(?:sa|nd))?(?:[\s-]+[1-4]\.\d)?(?:\s+international)?|creative\s+commons\s+attribution[\s-]+non[\s-]*commercial.*)$")),
    ("Public Domain", re.compile(r"^(?:public[\s-]+domain(?:\s+mark|\s+dedication)?(?:[\s-]+1\.0)?|(?:cc[\s-]+)?pdm(?:[\s-]+1\.0)?)$")),
    ("MIT", re.compile(r"^mit(?:\s+license)?$")),
    ("Apache-2.0", re.compile(r"^apache(?:[\s-]+license)?(?:[\s-]+2\.0)?$")),
    ("BSD", re.compile(r"^(?:0bsd|bsd(?:[\s-]+[23][\s-]+clause)?(?:\s+license)?)$")),
    ("OFL", re.compile(r"^(?:sil\s+)?(?:ofl|open\s+font\s+license)(?:[\s-]+1\.1)?$")),
    ("Pixabay", re.compile(r"^pixabay(?:\s+(?:content\s+)?license)?$")),
    ("Pexels", re.compile(r"^pexels(?:\s+license)?$")),
    ("Unsplash", re.compile(r"^unsplash(?:\s+license)?$")),
    ("Generated-Local", re.compile(r"^generated[\s-]+local$")),
    ("Owner-Supplied", re.compile(r"^owner[\s-]+supplied$")),
)

WRITTEN_PERMISSION_RE = re.compile(
    r"^used\s+with\s+written\s+permission(?:\s*(?:—|–|-|:|from|by|of)\s*|\s+)(?P<granter>.+)$"
)

SEARCH_URL_PATTERNS = (
    re.compile(r"/search(?:/|$|\?)", re.IGNORECASE),
    re.compile(r"/images/search(?:/|$|\?)", re.IGNORECASE),
    re.compile(r"/videos/search(?:/|$|\?)", re.IGNORECASE),
    re.compile(r"/s/photos/", re.IGNORECASE),
    re.compile(r"/s/videos/", re.IGNORECASE),
)

SEARCH_QUERY_KEYS = {"q", "query", "search", "s", "keyword", "keywords", "k"}


def normalize_licence_key(licence: str) -> str:
    raw = str(licence or "").strip().lower()
    raw = raw.replace("unlicenced", "unlicensed")
    raw = raw.replace("licenced", "licensed")
    raw = raw.replace("licence", "license")
    collapsed = " ".join(raw.replace("_", " ").split())
    return collapsed


def is_non_commercial_licence(licence: str | None) -> bool:
    norm = normalize_licence_key(str(licence or ""))
    for family, pat in ALLOW_LICENCE_FAMILIES:
        if family == "CC-BY-NC" and pat.match(norm):
            return True
    return False


def match_allowed_licence_family(norm: str) -> str | None:
    for family, pat in ALLOW_LICENCE_FAMILIES:
        if pat.match(norm):
            return family
    m = WRITTEN_PERMISSION_RE.match(norm)
    if m:
        granter = m.group("granter").strip()
        if sum(1 for ch in granter if ch.isalnum()) >= 2:
            return "Used with written permission"
    return None


def validate_licence(licence: str | None, local_path: str = "<asset>") -> str:
    cleaned = str(licence or "").strip()
    if not cleaned:
        raise AssetLicenceError(f"Asset '{local_path}' has no licence record.")
    if not any(ch.isalnum() for ch in cleaned):
        raise AssetLicenceError(
            f"Asset '{local_path}' uses invalid punctuation-only licence '{cleaned}'."
        )
    norm = normalize_licence_key(cleaned)
    if len(cleaned) < 3 or len(norm) < 3:
        raise AssetLicenceError(
            f"Asset '{local_path}' uses invalid licence '{cleaned}': licence string must be at least 3 characters."
        )

    norm_hyphen = re.sub(r"[\s-]+", "-", norm)
    norm_words = re.sub(r"[^a-z0-9/]+", " ", norm).strip()

    if norm in DENY_LICENCES or norm_hyphen in DENY_LICENCES:
        raise AssetLicenceError(
            f"Asset '{local_path}' uses denied licence '{cleaned}'."
        )
    for phrase in DENY_PHRASES:
        if re.search(rf"(?:^|\s){re.escape(phrase)}(?:\s|$)", norm_words):
            raise AssetLicenceError(
                f"Asset '{local_path}' uses denied licence '{cleaned}' (matched denied phrase '{phrase}')."
            )

    family = match_allowed_licence_family(norm)
    if family is None:
        raise AssetLicenceError(
            f"Asset '{local_path}' uses unrecognised licence '{cleaned}': not on the positive allow-list "
            "(accepted families: CC0, CC-BY, CC-BY-SA, CC-BY-NC [non-commercial], Public Domain, MIT, "
            "Apache-2.0, BSD, OFL, Pixabay, Pexels, Unsplash, or 'used with written permission — <Granter>')."
        )

    if family == "CC-BY-NC":
        print(
            f"WARNING: Asset '{local_path}' uses non-commercial licence '{cleaned}' "
            "(flagged as non-commercial: CC-BY-NC permits non-commercial use only).",
            file=sys.stderr,
        )
    return cleaned


def validate_source_url(source_url: str | None, local_path: str = "<asset>") -> str:
    cleaned = str(source_url or "").strip()
    if not cleaned:
        raise AssetLicenceError(f"Asset '{local_path}' is missing source_url.")
    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https", "local", "file"):
        raise AssetLicenceError(
            f"Asset '{local_path}' has invalid source_url scheme in '{cleaned}'."
        )
    if parsed.scheme in ("http", "https") and not parsed.netloc:
        raise AssetLicenceError(
            f"Asset '{local_path}' has invalid source_url host in '{cleaned}'."
        )
    for pat in SEARCH_URL_PATTERNS:
        if pat.search(parsed.path):
            raise AssetLicenceError(
                f"Asset '{local_path}' cites a search-results URL '{cleaned}'; cite the exact asset page."
            )
    query_params = parse_qs(parsed.query)
    if any(k.lower() in SEARCH_QUERY_KEYS for k in query_params):
        raise AssetLicenceError(
            f"Asset '{local_path}' cites a search query URL '{cleaned}'; cite the exact asset page."
        )
    return cleaned


def validate_entry(entry: dict[str, Any]) -> dict[str, Any]:
    local_path = str(entry.get("local_path") or entry.get("path") or "").strip()
    if not local_path:
        raise AssetLicenceError("Asset entry is missing local_path.")

    raw_licence = (
        entry.get("licence")
        if entry.get("licence") is not None
        else entry.get("license")
    )
    resolved_licence = validate_licence(raw_licence, local_path=local_path)
    resolved_url = validate_source_url(
        entry.get("source_url") or entry.get("url"),
        local_path=local_path,
    )
    author = str(entry.get("author") or entry.get("creator") or "").strip()
    if not author:
        raise AssetLicenceError(f"Asset '{local_path}' is missing author.")

    used_in = str(
        entry.get("used_in")
        or entry.get("where_used")
        or entry.get("usage")
        or ""
    ).strip()
    if not used_in:
        raise AssetLicenceError(f"Asset '{local_path}' is missing used_in.")

    result: dict[str, Any] = {
        "local_path": local_path,
        "source_url": resolved_url,
        "licence": resolved_licence,
        "author": author,
        "used_in": used_in,
    }
    if is_non_commercial_licence(resolved_licence):
        result["non_commercial"] = True
        result["licence_note"] = "NON-COMMERCIAL (CC-BY-NC): non-commercial use only"
    return result


class AssetLedger:
    def __init__(self, ledger_path: str | Path) -> None:
        self.ledger_path = Path(ledger_path)

    def list_entries(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        data = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "assets" in data:
            return list(data["assets"])
        if isinstance(data, list):
            return list(data)
        return []

    def _save_entries(self, entries: list[dict[str, Any]]) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "assets": entries}
        self.ledger_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def add(
        self,
        local_path: str,
        source_url: str,
        licence: str | None = None,
        author: str = "",
        used_in: str = "",
        *,
        license: str | None = None,
        where_used: str | None = None,
    ) -> dict[str, str]:
        validated = validate_entry(
            {
                "local_path": local_path,
                "source_url": source_url,
                "licence": licence if licence is not None else license,
                "author": author,
                "used_in": used_in or (where_used or ""),
            }
        )
        entries = [
            e for e in self.list_entries() if e.get("local_path") != validated["local_path"]
        ]
        entries.append(validated)
        self._save_entries(entries)
        return validated

    def verify(
        self,
        required_assets: list[str] | None = None,
        assets_dir: str | Path | None = None,
    ) -> list[dict[str, str]]:
        entries = self.list_entries()
        validated_entries: list[dict[str, str]] = []
        by_path: dict[str, dict[str, str]] = {}
        for raw in entries:
            v = validate_entry(raw)
            validated_entries.append(v)
            by_path[v["local_path"]] = v

        check_paths = list(required_assets or [])
        if assets_dir is not None:
            adir = Path(assets_dir)
            if adir.is_dir():
                for p in sorted(adir.rglob("*")):
                    if p.is_file() and p.name != self.ledger_path.name:
                        check_paths.append(str(p.relative_to(adir.parent)))

        for req in check_paths:
            norm = str(req).strip()
            if norm not in by_path:
                raise AssetLicenceError(
                    f"Asset '{norm}' is missing from the licence ledger."
                )
        return validated_entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ultron video pipeline asset licence ledger."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Record a licensed asset in the ledger.")
    p_add.add_argument("--ledger", required=True, help="Path to ledger JSON file.")
    p_add.add_argument("--local-path", required=True, help="Local asset path.")
    p_add.add_argument(
        "--source-url",
        required=True,
        help="Exact asset page URL (never a search-results URL).",
    )
    p_add.add_argument(
        "--licence",
        "--license",
        dest="licence",
        required=True,
        help="SPDX identifier or licence name (e.g. CC-BY-4.0, CC0-1.0, Pexels).",
    )
    p_add.add_argument("--author", required=True, help="Asset creator or attribution.")
    p_add.add_argument(
        "--used-in",
        "--where-used",
        dest="used_in",
        required=True,
        help="Scene ID or timestamp range where the asset is used.",
    )

    p_verify = sub.add_parser(
        "verify", help="Verify all ledger entries and required assets."
    )
    p_verify.add_argument("--ledger", required=True, help="Path to ledger JSON file.")
    p_verify.add_argument(
        "--asset",
        action="append",
        default=[],
        help="Asset path that must exist in the ledger (repeatable).",
    )
    p_verify.add_argument(
        "--assets-dir",
        default=None,
        help="Optional directory of assets to verify against the ledger.",
    )

    p_list = sub.add_parser("list", help="List recorded assets.")
    p_list.add_argument("--ledger", required=True, help="Path to ledger JSON file.")
    p_list.add_argument("--json", action="store_true", help="Output JSON.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ledger = AssetLedger(args.ledger)

    try:
        if args.command == "add":
            entry = ledger.add(
                local_path=args.local_path,
                source_url=args.source_url,
                licence=args.licence,
                author=args.author,
                used_in=args.used_in,
            )
            print(json.dumps(entry))
            return 0
        if args.command == "verify":
            entries = ledger.verify(
                required_assets=args.asset,
                assets_dir=args.assets_dir,
            )
            print(f"OK: {len(entries)} licensed asset(s) verified.")
            return 0
        if args.command == "list":
            entries = ledger.list_entries()
            if args.json:
                print(json.dumps(entries, indent=2))
            else:
                for e in entries:
                    print(
                        f"{e.get('local_path')}\t{e.get('licence')}\t"
                        f"{e.get('author')}\t{e.get('source_url')}\t{e.get('used_in')}"
                    )
            return 0
    except AssetLicenceError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
