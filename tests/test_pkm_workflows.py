"""Behavioral regressions for capture, review, and local-wrapper linking."""

import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
SKILLS = REPOSITORY / "skills"
WRAPPER = os.environ.get("PKM_TEST_WRAPPER")


class TemporaryVaultTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="pkm-workflow-test-")
        self.addCleanup(self.temporary.cleanup)
        self.vault = Path(self.temporary.name) / "test vault"
        self.vault.mkdir()
        self.environment = {**os.environ, "PKM_VALUT_DIR": str(self.vault), "PYTHONDONTWRITEBYTECODE": "1"}

    def note(self, relative, text):
        path = self.vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def script(self, skill, script, *args):
        return subprocess.run(
            [sys.executable, "-B", str(SKILLS / skill / "scripts" / script), *args],
            cwd=self.temporary.name, env=self.environment, capture_output=True, text=True,
        )


class CaptureTests(TemporaryVaultTests):
    def setUp(self):
        super().setUp()
        self.note("Templates/QuickAdd-PKM-AI-Conversation.md", """---
type: ai_conversation
created: {{DATE:YYYY-MM-DD HH:mm}}
---
# {{value:date}} {{value:title}}
## Context
{{value:context|type:multiline}}
## Prompt
{{value:prompt|type:multiline}}
## Raw Answer
{{value:raw_answer|type:multiline}}
## Actions
-
""")

    def capture(self, *extra):
        return self.script("pkm-capture", "capture_note.py", "--kind", "ai_conversation",
                           "--title", "主题", "--content", "保留 {{value:context}} 原文", *extra)

    def test_ai_uses_vault_template_and_preserves_multiline_context_and_literal_input(self):
        context = self.note("context.txt", "第一行\n第二行")
        result = self.capture("--context-file", str(context), "--prompt", "用户问题", "--date", "2026-11-24")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = Path(json.loads(result.stdout)["created"]).read_text()
        self.assertIn("第一行\n第二行", text)
        self.assertIn("用户问题", text)
        self.assertIn("保留 {{value:context}} 原文", text)
        self.assertIn("# 2026-11-24 主题", text)
        self.assertNotIn("- [ ]", text)
        self.assertNotIn("{{DATE:", text)

    def test_invalid_date_cannot_create_a_note_or_escape_directory(self):
        for value in ("2026-02-30", "2026-1-1", "../../escape"):
            with self.subTest(date=value):
                result = self.capture("--date", value)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.vault / "00_inbox").exists())

    def test_unknown_template_token_fails_without_creating_note(self):
        self.note("Templates/QuickAdd-PKM-AI-Conversation.md", "{{value:unknown}}")
        result = self.capture()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported template token", result.stderr)
        self.assertFalse((self.vault / "00_inbox").exists())

    def test_missing_template_fails_without_creating_note(self):
        (self.vault / "Templates/QuickAdd-PKM-AI-Conversation.md").unlink()
        result = self.capture()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.vault / "00_inbox").exists())

    def test_existing_note_is_preserved_and_unique_capture_does_not_overwrite_it(self):
        first = self.capture("--date", "2026-11-24")
        self.assertEqual(first.returncode, 0, first.stderr)
        path = Path(json.loads(first.stdout)["created"])
        original = path.read_bytes()
        self.assertNotEqual(self.capture("--date", "2026-11-24").returncode, 0)
        unique = self.capture("--date", "2026-11-24", "--unique")
        self.assertEqual(unique.returncode, 0, unique.stderr)
        self.assertNotEqual(json.loads(unique.stdout)["created"], str(path))
        self.assertEqual(path.read_bytes(), original)

    def test_inbox_capture_has_no_invented_task(self):
        result = self.script("pkm-capture", "capture_note.py", "--kind", "inbox",
                             "--title", "临时材料", "--content", "原文", "--context", "收集原因")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = Path(json.loads(result.stdout)["created"]).read_text()
        self.assertIn("收集原因", text)
        self.assertNotIn("- [ ]", text)


class ReviewTests(TemporaryVaultTests):
    def test_review_excludes_protected_and_processed_notes_and_distinguishes_open_claims(self):
        ai = "00_inbox/AI Conversations/"
        base = "---\ntype: ai_conversation\nstatus: inbox\n---\n# 对话\n"
        self.note(ai + "Raw.md", base + "## Extracted Value\n-\n## To Verify\n-\n")
        self.note(ai + "Processed.md", base.replace("status: inbox", "status: processed") + "## To Verify\n-\n")
        self.note(ai + "Linked.md", base + "## Related\n- Resource: [[03 Resources/方法]]\n## To Verify\n- 无。\n")
        self.note(ai + "Extracted.md", base + "## Extracted Value\n- [[03 Resources/方法]]\n## To Verify\n-\n")
        self.note(ai + "Verify.md", base + "## To Verify\n- 核对外部信息\n")
        self.note(ai + "Untitled.md", base)
        self.note(ai + "Welcome.md", base)
        self.note(ai + "test/Hidden.md", base)
        self.note(ai + ".stversions/Old.md", base)
        self.note(ai + "backup/Copy.md", base)
        before = {p: p.read_bytes() for p in self.vault.rglob("*.md")}
        result = self.script("pkm-review", "review_inbox.py", "--scope", "ai", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        groups = json.loads(result.stdout)
        self.assertEqual([x["file"] for x in groups["distill"]], [ai + "Raw.md"])
        self.assertEqual([x["file"] for x in groups["link"]], [ai + "Extracted.md"])
        self.assertEqual([x["file"] for x in groups["verify"]], [ai + "Verify.md"])
        self.assertEqual(groups["triage"], [])
        self.assertEqual({p: p.read_bytes() for p in self.vault.rglob("*.md")}, before)

    def test_fenced_examples_do_not_invent_verification_items(self):
        classify = runpy.run_path(str(SKILLS / "pkm-review/scripts/review_inbox.py"))["classify"]
        text = "---\ntype: ai_conversation\n---\n```md\n## To Verify\n- 示例\n```\n## To Verify\n-\n"
        self.assertEqual(classify(Path("Raw.md"), text), "distill")

    def test_raw_decisions_and_extraction_candidates_still_need_distillation(self):
        classify = runpy.run_path(str(SKILLS / "pkm-review/scripts/review_inbox.py"))["classify"]
        base = "---\ntype: ai_conversation\nstatus: inbox\n---\n"
        for content in ("## Decisions\n- 采用当前方案\n", "## Extracted Value\n- 可提炼为方法\n"):
            with self.subTest(content=content):
                self.assertEqual(classify(Path("Raw.md"), base + content), "distill")


@unittest.skipUnless(WRAPPER, "Set PKM_TEST_WRAPPER to enable current-vault wrapper integration")
class LinkIntegrationTests(TemporaryVaultTests):
    def setUp(self):
        super().setUp()
        self.note("scripts/pkm_quickadd.py", Path(WRAPPER).read_text())
        self.note("MOCs/主题.md", "# 主题\n\n## Notes\n- [[03 Resources/方法]]\n\n## 已沉淀资源\n")
        self.note("01 Projects/项目.md", "---\ntype: project\nstatus: active\n---\n\n## Next Actions\n\n## Resources\n")

    def link(self, file="MOCs/主题.md", heading="已沉淀资源", *extra):
        return self.script("pkm-link", "update_links.py", "--file", file, "--heading", heading,
                           "--entry", "- [[03 Resources/方法]]", *extra)

    def test_link_in_other_section_does_not_suppress_target_and_retry_is_noop(self):
        first = self.link()
        self.assertEqual(first.returncode, 0, first.stderr)
        path = self.vault / "MOCs/主题.md"
        text = path.read_text()
        self.assertIn("## 已沉淀资源\n- [[03 Resources/方法]]", text)
        self.assertEqual(text.count("[[03 Resources/方法]]"), 2)
        again = self.link()
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertTrue(json.loads(again.stdout)["duplicate"])
        self.assertEqual(path.read_text(), text)

    def test_project_resource_link_uses_wrapper(self):
        result = self.link("01 Projects/项目.md", "Resources")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Resources\n- [[03 Resources/方法]]", (self.vault / "01 Projects/项目.md").read_text())

    def test_missing_target_or_heading_is_not_silently_created(self):
        original = (self.vault / "MOCs/主题.md").read_bytes()
        self.assertNotEqual(self.link(heading="Missing").returncode, 0)
        self.assertEqual((self.vault / "MOCs/主题.md").read_bytes(), original)
        self.assertNotEqual(self.link(file="MOCs/Missing.md").returncode, 0)
        self.assertFalse((self.vault / "MOCs/Missing.md").exists())

    def test_wrapper_missing_fails_without_direct_write(self):
        (self.vault / "scripts/pkm_quickadd.py").unlink()
        before = (self.vault / "MOCs/主题.md").read_bytes()
        self.assertNotEqual(self.link().returncode, 0)
        self.assertEqual((self.vault / "MOCs/主题.md").read_bytes(), before)

    def test_check_only_is_read_only(self):
        path = self.vault / "MOCs/主题.md"
        before = path.read_bytes()
        result = self.link("MOCs/主题.md", "已沉淀资源", "--check-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["would_change"])
        self.assertEqual(path.read_bytes(), before)

    def test_generic_resource_writes_are_rejected(self):
        self.assertNotEqual(self.link("03 Resources/方法.md", "Related").returncode, 0)
        self.assertFalse((self.vault / "03 Resources").exists())


if __name__ == "__main__":
    unittest.main()
