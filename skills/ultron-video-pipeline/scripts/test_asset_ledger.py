#!/usr/bin/env python3
"""Tests for scripts/asset_ledger.py."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import asset_ledger  # noqa: E402


class TestAssetLedger(unittest.TestCase):
    def test_valid_cc_by_entry_passes_and_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_file = Path(tmpdir) / "assets_ledger.json"
            ledger = asset_ledger.AssetLedger(ledger_file)

            entry = ledger.add(
                local_path="assets/broll_datacenter.mp4",
                source_url="https://commons.wikimedia.org/wiki/File:CERN_Datacenter.mp4",
                licence="CC-BY-4.0",
                author="CERN Media Archive",
                used_in="scene-02 (00:08-00:14)",
            )

            self.assertEqual(entry["local_path"], "assets/broll_datacenter.mp4")
            self.assertEqual(entry["licence"], "CC-BY-4.0")

            reloaded = asset_ledger.AssetLedger(ledger_file)
            entries = reloaded.list_entries()
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["local_path"], "assets/broll_datacenter.mp4")
            self.assertEqual(
                entries[0]["source_url"],
                "https://commons.wikimedia.org/wiki/File:CERN_Datacenter.mp4",
            )
            self.assertEqual(entries[0]["licence"], "CC-BY-4.0")
            self.assertEqual(entries[0]["author"], "CERN Media Archive")
            self.assertEqual(entries[0]["used_in"], "scene-02 (00:08-00:14)")

    def test_unlicensed_asset_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_file = Path(tmpdir) / "assets_ledger.json"
            ledger = asset_ledger.AssetLedger(ledger_file)

            with self.assertRaises(asset_ledger.AssetLicenceError):
                ledger.add(
                    local_path="assets/mystery.png",
                    source_url="https://example.org/assets/mystery-card",
                    licence="",
                    author="Jane Doe",
                    used_in="scene-01",
                )

            with self.assertRaises(asset_ledger.AssetLicenceError):
                ledger.add(
                    local_path="assets/mystery2.png",
                    source_url="https://example.org/assets/mystery-card-2",
                    licence=None,
                    author="Jane Doe",
                    used_in="scene-01",
                )

            with self.assertRaises(asset_ledger.AssetLicenceError):
                ledger.verify(required_assets=["assets/unrecorded.png"])

    def test_denied_licence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_file = Path(tmpdir) / "assets_ledger.json"
            ledger = asset_ledger.AssetLedger(ledger_file)

            for bad_licence in (
                "All Rights Reserved",
                "all-rights-reserved",
                "unknown",
                "UNKNOWN",
                "unlicensed",
                "proprietary",
                "none",
                "N/A",
            ):
                with self.subTest(licence=bad_licence):
                    with self.assertRaises(asset_ledger.AssetLicenceError):
                        ledger.add(
                            local_path="assets/stock_clip.mp4",
                            source_url="https://example.org/videos/stock-clip-42",
                            licence=bad_licence,
                            author="Studio Corp",
                            used_in="scene-03",
                        )

    def test_search_results_url_and_missing_provenance_fields_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_file = Path(tmpdir) / "assets_ledger.json"
            ledger = asset_ledger.AssetLedger(ledger_file)

            for search_url in (
                "https://www.google.com/search?q=datacenter+broll",
                "https://www.pexels.com/search/ai/",
                "https://unsplash.com/s/photos/robot",
                "https://pixabay.com/images/search/server/",
            ):
                with self.subTest(url=search_url):
                    with self.assertRaises(asset_ledger.AssetLicenceError):
                        ledger.add(
                            local_path="assets/clip.mp4",
                            source_url=search_url,
                            licence="CC0-1.0",
                            author="John Doe",
                            used_in="scene-01",
                        )

            with self.assertRaises(asset_ledger.AssetLicenceError):
                ledger.add(
                    local_path="assets/clip.mp4",
                    source_url="",
                    licence="CC0-1.0",
                    author="John Doe",
                    used_in="scene-01",
                )

            with self.assertRaises(asset_ledger.AssetLicenceError):
                ledger.add(
                    local_path="assets/clip.mp4",
                    source_url="https://commons.wikimedia.org/wiki/File:Clip.mp4",
                    licence="CC0-1.0",
                    author="",
                    used_in="scene-01",
                )

            with self.assertRaises(asset_ledger.AssetLicenceError):
                ledger.add(
                    local_path="assets/clip.mp4",
                    source_url="https://commons.wikimedia.org/wiki/File:Clip.mp4",
                    licence="CC0-1.0",
                    author="John Doe",
                    used_in="",
                )

    def test_cli_add_and_verify(self) -> None:
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_file = Path(tmpdir) / "assets_ledger.json"
            out = io.StringIO()
            err = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc_add = asset_ledger.main(
                    [
                        "add",
                        "--ledger",
                        str(ledger_file),
                        "--local-path",
                        "assets/diagram.svg",
                        "--source-url",
                        "https://commons.wikimedia.org/wiki/File:Transformer_architecture.svg",
                        "--licence",
                        "CC-BY-SA-4.0",
                        "--author",
                        "Wikimedia Contributor",
                        "--used-in",
                        "scene-01 (00:00-00:05)",
                    ]
                )
            self.assertEqual(rc_add, 0)

            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc_verify_ok = asset_ledger.main(
                    [
                        "verify",
                        "--ledger",
                        str(ledger_file),
                        "--asset",
                        "assets/diagram.svg",
                    ]
                )
            self.assertEqual(rc_verify_ok, 0)

            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc_verify_missing = asset_ledger.main(
                    [
                        "verify",
                        "--ledger",
                        str(ledger_file),
                        "--asset",
                        "assets/missing_broll.mp4",
                    ]
                )
            self.assertNotEqual(rc_verify_missing, 0)

    def test_fail_closed_refuses_no_licence_stated_and_unknown_phrases_and_unrecognised(self) -> None:
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_file = Path(tmpdir) / "assets_ledger.json"
            ledger = asset_ledger.AssetLedger(ledger_file)

            for refused_licence in (
                "no licence stated",
                "no license stated",
                "licensed as unknown",
                "licenced as unknown",
                "unclear",
                "licence is unclear",
                "see website",
                "please see website for license",
                "all rights reserved by author",
                "proprietary commercial licence",
                "none stated",
                "some made-up custom permission",
                "used with written permission",
                "used with written permission — ---",
            ):
                with self.subTest(licence=refused_licence):
                    with self.assertRaises(asset_ledger.AssetLicenceError):
                        ledger.add(
                            local_path="assets/test.mp4",
                            source_url="https://example.org/assets/test-42",
                            licence=refused_licence,
                            author="Test Author",
                            used_in="scene-01",
                        )

            # Verify CLI exits non-zero and prints reason on stderr for "no licence stated"
            out = io.StringIO()
            err = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = asset_ledger.main(
                    [
                        "add",
                        "--ledger",
                        str(ledger_file),
                        "--local-path",
                        "assets/bad.mp4",
                        "--source-url",
                        "https://example.org/assets/bad",
                        "--licence",
                        "no licence stated",
                        "--author",
                        "Author",
                        "--used-in",
                        "scene-01",
                    ]
                )
            self.assertNotEqual(rc, 0)
            self.assertIn("REFUSED:", err.getvalue())

    def test_short_and_punctuation_only_licences_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_file = Path(tmpdir) / "assets_ledger.json"
            ledger = asset_ledger.AssetLedger(ledger_file)

            for bad_licence in ("CC", "PD", "OK", "x", "---", "???", "..."):
                with self.subTest(licence=bad_licence):
                    with self.assertRaises(asset_ledger.AssetLicenceError):
                        ledger.add(
                            local_path="assets/short.png",
                            source_url="https://example.org/assets/short",
                            licence=bad_licence,
                            author="Author",
                            used_in="scene-01",
                        )

    def test_allow_list_accepts_known_families_case_insensitively(self) -> None:
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_file = Path(tmpdir) / "assets_ledger.json"
            ledger = asset_ledger.AssetLedger(ledger_file)

            for allowed_licence in (
                "CC-BY-4.0",
                "cc-by-4.0",
                "CC0-1.0",
                "cc0-1.0",
                "CC-BY-SA-4.0",
                "Pexels License",
                "pexels licence",
                "Pixabay License",
                "Unsplash License",
                "Public Domain",
                "public domain",
                "MIT",
                "mit",
                "Apache-2.0",
                "apache-2.0",
                "BSD-3-Clause",
                "OFL-1.1",
                "used with written permission — Acme Ltd",
                "USED WITH WRITTEN PERMISSION — Acme Ltd",
                "used with written permission: Jane Doe Studios",
            ):
                with self.subTest(licence=allowed_licence):
                    entry = ledger.add(
                        local_path="assets/ok.mp4",
                        source_url="https://commons.wikimedia.org/wiki/File:Ok.mp4",
                        licence=allowed_licence,
                        author="Acme Creator",
                        used_in="scene-01 (00:00-00:04)",
                    )
                    self.assertEqual(entry["licence"], allowed_licence)

            # Verify CC-BY-NC is accepted and explicitly flagged as non-commercial
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                nc_entry = ledger.add(
                    local_path="assets/nc_track.mp3",
                    source_url="https://example.org/audio/nc_track",
                    licence="CC-BY-NC-4.0",
                    author="Indie Musician",
                    used_in="scene-02 (00:04-00:10)",
                )
            self.assertTrue(nc_entry.get("non_commercial"))
            self.assertIn("non-commercial", err.getvalue().lower())


if __name__ == "__main__":
    unittest.main()

