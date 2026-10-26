#!/usr/bin/env python3
"""Tests for scripts/corpus_index.py."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import corpus_index  # noqa: E402


class TestCorpusIndex(unittest.TestCase):
    def test_normal_markdown_file_is_findable_by_full_text_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root_a = Path(tmpdir) / "Knowledge"
            root_a.mkdir(parents=True)
            doc_path = root_a / "ai-video-trends-2026.md"
            doc_path.write_text(
                "# AI Video Trends 2026\n\n"
                "HyperFrames deterministic seekable timelines outperform raw canvas loops.\n",
                encoding="utf-8",
            )

            db_path = Path(tmpdir) / "corpus.db"
            counts = corpus_index.build_index(db_path=db_path, roots=[root_a])
            self.assertEqual(counts[str(root_a)], 1)

            hits = corpus_index.search_index(db_path=db_path, query="seekable timelines")
            self.assertEqual(len(hits), 1)
            self.assertEqual(Path(hits[0]["path"]).resolve(), doc_path.resolve())

    def test_secret_paths_and_secret_contents_are_not_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root_a = Path(tmpdir) / "Knowledge"
            root_a.mkdir(parents=True)

            # Secret-looking filenames that MUST be skipped
            (root_a / ".env").write_text("OPENAI_API_KEY=supersecretvalue123\n", encoding="utf-8")
            (root_a / ".env.production").write_text("PROD_KEY=[REDACTED]\n", encoding="utf-8")
            (root_a / "token.json").write_text('{"access_token": "[REDACTED]"}', encoding="utf-8")
            (root_a / "oauth-token.yaml").write_text("token: [REDACTED]\n", encoding="utf-8")
            (root_a / "credentials.json").write_text('{"client_secret": "shh"}', encoding="utf-8")
            (root_a / "auth.json").write_text('{"cookie": "session_cookie_val"}', encoding="utf-8")

            # Normal filename but contains a secret token pattern in body
            (root_a / "leaked-note.md").write_text(
                "# Leaked Note\nKey is sk-or-v[REDACTED_PHONE]abcdef[REDACTED_PHONE]abcdef\n",
                encoding="utf-8",
            )

            # Safe markdown file
            safe_doc = root_a / "clean-report.md"
            safe_doc.write_text(
                "# Clean Report\nManim mathematical animations explain linear algebra clearly.\n",
                encoding="utf-8",
            )

            db_path = Path(tmpdir) / "corpus.db"
            counts = corpus_index.build_index(db_path=db_path, roots=[root_a])

            self.assertEqual(counts[str(root_a)], 1)
            self.assertEqual(corpus_index.search_index(db_path, "supersecretvalue123"), [])
            self.assertEqual(corpus_index.search_index(db_path, "[REDACTED]"), [])
            self.assertEqual(corpus_index.search_index(db_path, "tok_yaml_xyz"), [])
            self.assertEqual(corpus_index.search_index(db_path, "session_cookie_val"), [])
            self.assertEqual(corpus_index.search_index(db_path, "Leaked"), [])

            clean_hits = corpus_index.search_index(db_path, "Manim mathematical")
            self.assertEqual(len(clean_hits), 1)
            self.assertEqual(Path(clean_hits[0]["path"]).resolve(), safe_doc.resolve())

    def test_counts_match_fixture_and_cli_search_works(self) -> None:
        import contextlib
        import io
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            r1 = Path(tmpdir) / "Obsidian_Knowledge"
            r2 = Path(tmpdir) / "research_reports"
            r3 = Path(tmpdir) / "reports_md"
            r1.mkdir()
            r2.mkdir()
            r3.mkdir()

            (r1 / "note1.md").write_text("# Note One\nKinetic typography hooks viewers.\n", encoding="utf-8")
            (r1 / "note2.md").write_text("# Note Two\nVoiceover pacing at 150 wpm.\n", encoding="utf-8")
            (r1 / ".env").write_text("SECRET=[REDACTED]\n", encoding="utf-8")

            (r2 / "report1.md").write_text("# Report Alpha\nB-roll provenance ledger rules.\n", encoding="utf-8")
            (r2 / "token.json").write_text('{"token": "hidden"}', encoding="utf-8")

            (r3 / "digest1.md").write_text("# Digest One\nRemotion vs HyperFrames comparison.\n", encoding="utf-8")
            (r3 / "digest2.md").write_text("# Digest Two\nCaptions sync within 50ms.\n", encoding="utf-8")
            (r3 / "digest3.md").write_text("# Digest Three\nAudio loudness at -14 LUFS.\n", encoding="utf-8")

            db_path = Path(tmpdir) / "corpus.db"
            counts = corpus_index.build_index(db_path=db_path, roots=[r1, r2, r3])
            self.assertEqual(counts[str(r1)], 2)
            self.assertEqual(counts[str(r2)], 1)
            self.assertEqual(counts[str(r3)], 3)

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = corpus_index.main(
                    [
                        "search",
                        "HyperFrames comparison",
                        "--db",
                        str(db_path),
                        "--json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(out.getvalue())
            self.assertEqual(len(payload["results"]), 1)
            self.assertIn("digest1.md", payload["results"][0]["path"])
            self.assertEqual(payload["counts"][str(r1)], 2)
            self.assertEqual(payload["counts"][str(r2)], 1)
            self.assertEqual(payload["counts"][str(r3)], 3)

    def test_default_roots_match_ultron_scope(self) -> None:
        self.assertEqual(
            list(corpus_index.DEFAULT_ROOTS),
            [
                "[REDACTED_PATH]",
                "[REDACTED_PATH]",
                "[REDACTED_PATH]",
                "[REDACTED_PATH]",
                "[REDACTED_PATH]",
            ],
        )

    def test_discord_github_aws_slack_bearer_and_high_entropy_excluded_and_counted(self) -> None:
        import contextlib
        import io
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            root_a = Path(tmpdir) / "Knowledge"
            root_a.mkdir(parents=True)

            # 1. Discord bot token (base64 + . + base64 + . + 38-char base64url)
            (root_a / "discord_bot.md").write_text(
                "# Discord Bot Config\n"
                "Token: [REDACTED]\n",
                encoding="utf-8",
            )
            # 2. GitHub ghp_ token
            (root_a / "github_note.md").write_text(
                "# GitHub Deploy\n"
                "Use ghp_[REDACTED_PHONE]abcdefABCDEF[REDACTED_PHONE]abcd to push.\n",
                encoding="utf-8",
            )
            # 3. AWS AKIA access key id
            (root_a / "aws_note.md").write_text(
                "# AWS Storage\n"
                "Key ID: AKIA[REDACTED_PHONE]ABCDEF\n",
                encoding="utf-8",
            )
            # 4. Slack xoxb- token
            (root_a / "slack_note.md").write_text(
                "# Slack Bot\n"
                "Bot token: [REDACTED]\n",
                encoding="utf-8",
            )
            # 5. Bearer <40 chars>
            (root_a / "bearer_note.md").write_text(
                "# Auth Header\n"
                "Authorization: Bearer [REDACTED]\n",
                encoding="utf-8",
            )
            # 6. Additional required patterns: Discord webhook, GitHub gho_/ghu_/ghs_/ghr_, aws_secret, Stripe, SendGrid, Google AIza, high-entropy 32+ char token, secret-ish markdown filename
            (root_a / "webhook_note.md").write_text(
                "Webhook: https://discord.com/api/webhooks/[REDACTED_PHONE]/aBcDeFgHiJkLmNoPqRsTuVwXyZ[REDACTED_PHONE]\n",
                encoding="utf-8",
            )
            (root_a / "stripe_sg_note.md").write_text(
                "Stripe: [REDACTED_STRIPE_KEY]\n"
                "SendGrid: SG.abcdefghijklmnopqrstuv.[REDACTED_PHONE]abcdefghijkl\n",
                encoding="utf-8",
            )
            (root_a / "high_entropy_note.md").write_text(
                "# Random Secret\n"
                "Raw secret value: q9Wm2Xp7Vz4Bn8Cf1Hj5Wd3Yg6Ts0Na9Mk4Lp2\n",
                encoding="utf-8",
            )
            (root_a / "my_secret_notes.md").write_text(
                "# Normal looking body in a secret-named file\n",
                encoding="utf-8",
            )

            # 7. Normal markdown file (MUST be indexed and findable)
            normal_doc = root_a / "normal_guide.md"
            normal_doc.write_text(
                "# Normal Guide\n\n"
                "Deterministic frame rendering keeps motion graphics rock solid.\n",
                encoding="utf-8",
            )

            # 8. Placeholder inside a fenced code block (MUST be allowed and indexed)
            fence_doc = root_a / "api_placeholder_docs.md"
            fence_doc.write_text(
                "# API Placeholder Documentation\n\n"
                "Configure your local environment with placeholders:\n\n"
                "```bash\n"
                "export MY_KEY=\"YOUR_KEY_HERE_[REDACTED_PHONE]abcdefABCDEF\"\n"
                "curl -H \"Authorization: Bearer <token>\" https://api.example.com/v1\n"
                "export DUMMY_TOKEN=\"xxx_placeholder_token_AbCdEfGh[REDACTED_PHONE]IjKlMnOpQrStUvWxYz\"\n"
                "```\n",
                encoding="utf-8",
            )

            db_path = Path(tmpdir) / "corpus.db"
            counts = corpus_index.build_index(db_path=db_path, roots=[root_a])

            # Only the 2 safe markdown files should be indexed
            self.assertEqual(counts[str(root_a)], 2)
            # All 9 secret files must be counted as withheld/excluded
            self.assertEqual(counts.withheld, 9)
            self.assertEqual(counts.excluded, 9)
            self.assertEqual(counts.withheld_by_root[str(root_a)], 9)

            # Verify secret tokens are NOT searchable
            for secret_query in (
                "MTIzNDU2Nzg5MDEyMzQ1Njc4",
                "Discord Bot Config",
                "ghp_[REDACTED_PHONE]abcdefABCDEF[REDACTED_PHONE]abcd",
                "AKIA[REDACTED_PHONE]ABCDEF",
                "xoxb",
                "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8s9T0",
                "[REDACTED_STRIPE_KEY]",
                "[REDACTED]",
            ):
                with self.subTest(query=secret_query):
                    self.assertEqual(corpus_index.search_index(db_path, secret_query), [])

            # Verify normal markdown file is findable
            normal_hits = corpus_index.search_index(db_path, "Deterministic frame rendering")
            self.assertEqual(len(normal_hits), 1)
            self.assertEqual(Path(normal_hits[0]["path"]).resolve(), normal_doc.resolve())

            # Verify fenced placeholder file is allowed and findable
            fence_hits = corpus_index.search_index(db_path, "API Placeholder Documentation")
            self.assertEqual(len(fence_hits), 1)
            self.assertEqual(Path(fence_hits[0]["path"]).resolve(), fence_doc.resolve())

            # Also verify CLI build reports withheld count in JSON and text modes
            out_json = io.StringIO()
            err_json = io.StringIO()
            with contextlib.redirect_stdout(out_json), contextlib.redirect_stderr(err_json):
                rc = corpus_index.main(["build", "--db", str(db_path), "--root", str(root_a), "--json"])
            self.assertEqual(rc, 0)
            build_payload = json.loads(out_json.getvalue())
            self.assertEqual(build_payload["withheld"], 9)
            self.assertEqual(build_payload["withheld_by_root"][str(root_a)], 9)

    def test_all_secret_variants_and_fenced_real_secret_refused(self) -> None:
        # Every required token family must be flagged by has_secret_content
        for sample in (
            "gho_[REDACTED_PHONE]abcdefABCDEF[REDACTED_PHONE]abcd",
            "ghu_[REDACTED_PHONE]abcdefABCDEF[REDACTED_PHONE]abcd",
            "ghs_[REDACTED_PHONE]abcdefABCDEF[REDACTED_PHONE]abcd",
            "ghr_[REDACTED_PHONE]abcdefABCDEF[REDACTED_PHONE]abcd",
            "github_pat_11ABCDEFG[REDACTED_PHONE]_abcdefghijklmnopqrstuvwxyz[REDACTED_PHONE]",
            "aws_secret_access_key = [REDACTED]",
            "xoxp-[REDACTED_PHONE]-aBcDeFgHiJkLmNoPqRsTuVwX",
            "xoxa-[REDACTED_PHONE]-aBcDeFgHiJkLmNoPqRsTuVwX",
            "[REDACTED_STRIPE_RESTRICTED_KEY]",
            "AIzaSyA[REDACTED_PHONE]abcdefABCDEF[REDACTED_PHONE]",
            # A real secret on the same fenced line as a placeholder must STILL be refused
            "```bash\ncurl -H 'X-Note: YOUR_KEY_HERE' -H 'Authorization: Bearer [REDACTED]'\n```",
            # A real high-entropy token inside a fence (not a placeholder) must STILL be refused
            "```bash\n TOKEN_VAL=q9Wm2Xp7Vz4Bn8Cf1Hj5Wd3Yg6Ts0Na9Mk4Lp2\n```",
        ):
            with self.subTest(sample=sample):
                self.assertTrue(corpus_index.has_secret_content(sample))

    def test_ultron_skill_relative_links_resolve(self) -> None:
        import re

        repo_root = Path(HERE).resolve().parent
        skill_md_path = repo_root / "skills" / "creative" / "ultron-video-pipeline" / "SKILL.md"
        text = skill_md_path.read_text(encoding="utf-8")
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
        self.assertGreater(len(links), 20)

        installed_skill_dir = Path("[REDACTED_PATH]")
        for label, target in links:
            with self.subTest(label=label, target=target):
                if target.startswith("references/"):
                    resolved = (skill_md_path.parent / target).resolve()
                else:
                    resolved = (installed_skill_dir / target).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"Relative link [{label}]({target}) does not exist at {resolved}",
                )

    def test_ultron_skill_forbids_third_party_download_and_recut(self) -> None:
        import re

        repo_root = Path(HERE).resolve().parent
        skill_dir = repo_root / "skills" / "creative" / "ultron-video-pipeline"
        skill_md_path = skill_dir / "SKILL.md"
        intake_md_path = skill_dir / "references" / "intake-questions.md"

        docs = [skill_md_path, *sorted((skill_dir / "references").glob("*.md"))]
        forbidden_phrases = (
            "yt-dlp",
            "youtube-dl",
            "download the source video",
            "download a source video",
            "reaction recut",
            "reaction/recut",
            "source intake",
            "pause frames over a source video",
            "talking-head-recut",
        )
        for doc in docs:
            content_lower = doc.read_text(encoding="utf-8").lower()
            for phrase in forbidden_phrases:
                with self.subTest(doc=doc.name, phrase=phrase):
                    self.assertNotIn(
                        phrase,
                        content_lower,
                        f"Forbidden fetch/recut phrase {phrase!r} found in {doc}",
                    )

        skill_text = skill_md_path.read_text(encoding="utf-8")
        self.assertIn("### Stage (4) GENERATE VISUALS", skill_text)
        self.assertNotIn("### Stage (4) ASSET SOURCING", skill_text)
        self.assertIn("scene-01-sample.mp4", skill_text)
        self.assertIn("Recipe: Build a Full 2–3 Minute Generative Video", skill_text)

        intake_text = intake_md_path.read_text(encoding="utf-8")
        numbered_questions = re.findall(r"^\d+\.\s+\*\*", intake_text, flags=re.MULTILINE)
        self.assertGreaterEqual(len(numbered_questions), 1)
        self.assertLessEqual(len(numbered_questions), 7)
        self.assertIn("you decide", intake_text.lower())


if __name__ == "__main__":
    unittest.main()


