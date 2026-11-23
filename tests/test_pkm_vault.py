"""Exercise vault selection from an unrelated working directory."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
COMMANDS = {
    "capture": [
        "pkm-capture/scripts/capture_note.py",
        "--kind", "inbox", "--title", "Captured", "--content", "Raw content",
    ],
    "link": [
        "pkm-link/scripts/update_links.py",
        "--file", "MOCs/Index.md", "--heading", "Links", "--entry", "- [[Resource]]",
    ],
    "review": ["pkm-review/scripts/review_inbox.py", "--scope", "inbox", "--json"],
}


class VaultSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="pkm-vault-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.vault = self.root / "target vault"
        (self.vault / "00_inbox").mkdir(parents=True)
        (self.vault / "00_inbox/Seed.md").write_text("# Seed\n", encoding="utf-8")
        (self.vault / "scripts").mkdir()
        (self.vault / "scripts/pkm_quickadd.py").write_text(
            "import json, os, sys\n"
            "args = sys.argv[1:]\n"
            "print(json.dumps({'action': args[0], 'cwd': os.getcwd(), "
            "'vault_root': args[args.index('--vault-root') + 1], "
            "'payload': json.loads(args[args.index('--payload-json') + 1])}))\n",
            encoding="utf-8",
        )
        self.workspace = self.root / "unrelated workspace"
        (self.workspace / "00_inbox").mkdir(parents=True)
        (self.workspace / "00_inbox/Wrong.md").write_text("# Wrong vault\n", encoding="utf-8")

    def run_script(self, name, *, value=None, extra=(), configured=True):
        command = COMMANDS[name]
        environment = os.environ.copy()
        environment.pop("PKM_VALUT_DIR", None)
        if configured:
            environment["PKM_VALUT_DIR"] = str(self.vault) if value is None else value
        return subprocess.run(
            [sys.executable, str(REPOSITORY / "skills" / command[0]), *command[1:], *extra],
            cwd=self.workspace,
            env=environment,
            capture_output=True,
            text=True,
        )

    def snapshot(self):
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }

    def test_unset_variable_rejects_even_an_explicit_vault(self):
        before = self.snapshot()
        for name in COMMANDS:
            with self.subTest(script=name):
                result = self.run_script(name, configured=False, extra=["--vault", str(self.vault)])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("PKM_VALUT_DIR", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_invalid_roots_fail_without_reading_or_writing_workspace(self):
        values = ["", " ", ".", "../target vault", str(self.root / "missing"), str(self.vault / "00_inbox/Seed.md")]
        before = self.snapshot()
        for name in COMMANDS:
            for value in values:
                with self.subTest(script=name, value=value):
                    result = self.run_script(name, value=value)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("PKM_VALUT_DIR", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_capture_link_and_review_use_environment_from_another_cwd(self):
        capture = self.run_script("capture")
        self.assertEqual(capture.returncode, 0, capture.stderr)
        created = Path(json.loads(capture.stdout)["created"])
        self.assertEqual(created, self.vault / "00_inbox/Captured.md")
        self.assertIn("Raw content", created.read_text())

        link = self.run_script("link")
        self.assertEqual(link.returncode, 0, link.stderr)
        delegated = json.loads(link.stdout)
        self.assertEqual(delegated["action"], "append-moc-link")
        self.assertEqual(delegated["vault_root"], str(self.vault))
        self.assertEqual(delegated["cwd"], str(self.vault))
        self.assertEqual(delegated["payload"], {"file": "MOCs/Index.md", "heading": "Links", "entry": "- [[Resource]]"})

        review = self.run_script("review")
        self.assertEqual(review.returncode, 0, review.stderr)
        files = {item["file"] for group in json.loads(review.stdout).values() for item in group}
        self.assertEqual(files, {"00_inbox/Seed.md", "00_inbox/Captured.md"})
        self.assertEqual(list((self.workspace / "00_inbox").iterdir()), [self.workspace / "00_inbox/Wrong.md"])
        self.assertFalse((self.workspace / "MOCs").exists())

    def test_explicit_vault_cannot_redirect_an_environment_bound_run(self):
        before = self.snapshot()
        for name in COMMANDS:
            with self.subTest(script=name):
                result = self.run_script(name, extra=["--vault", str(self.workspace)])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("PKM_VALUT_DIR", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_explicit_matching_vault_is_still_accepted(self):
        for name in COMMANDS:
            with self.subTest(script=name):
                result = self.run_script(name, extra=["--vault", str(self.vault)])
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_environment_can_select_a_symlink_to_a_vault(self):
        alias = self.root / "vault alias"
        alias.symlink_to(self.vault, target_is_directory=True)
        result = self.run_script("capture", value=str(alias))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(json.loads(result.stdout)["created"]), self.vault / "00_inbox/Captured.md")

    def test_link_rejects_parent_sibling_prefix_and_symlink_escape(self):
        outside = self.root / "target vault sibling"
        outside.mkdir()
        (self.vault / "Outside").symlink_to(outside, target_is_directory=True)
        before = self.snapshot()
        for target in ["../target vault sibling/Escape.md", str(outside / "Escape.md"), "Outside/Escape.md"]:
            with self.subTest(target=target):
                result = self.run_script("link", extra=["--file", target])
                self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_capture_rejects_an_inbox_symlink_outside_vault(self):
        outside = self.root / "outside"
        outside.mkdir()
        # Use a second vault so its inbox can be a symlink from the outset.
        second = self.root / "second vault"
        second.mkdir()
        (second / "00_inbox").symlink_to(outside, target_is_directory=True)
        result = self.run_script("capture", value=str(second))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(outside.iterdir()), [])

    def test_capture_rejects_a_note_symlink_outside_vault(self):
        outside = self.root / "Outside.md"
        (self.vault / "00_inbox/Captured.md").symlink_to(outside)
        result = self.run_script("capture")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(outside.exists())

    def test_review_rejects_a_note_symlink_outside_vault(self):
        outside = self.root / "Outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        (self.vault / "00_inbox/Outside.md").symlink_to(outside)
        result = self.run_script("review")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_review_rejects_an_inbox_symlink_outside_vault(self):
        second = self.root / "second vault"
        second.mkdir()
        (second / "00_inbox").symlink_to(self.workspace / "00_inbox", target_is_directory=True)
        result = self.run_script("review", value=str(second))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


class DocumentedWrapperTests(unittest.TestCase):
    def test_examples_anchor_wrappers_and_reject_invalid_configuration(self):
        with tempfile.TemporaryDirectory(prefix="pkm-wrapper-test-") as temporary:
            root = Path(temporary)
            vault = root / "configured vault"
            (vault / "scripts").mkdir(parents=True)
            workspace = root / "another workspace"
            workspace.mkdir()
            stub = (
                "import argparse, json, os, sys\n"
                "parser = argparse.ArgumentParser()\n"
                "parser.add_argument('--vault-root', default=os.environ['PKM_VAULT'])\n"
                "options, _ = parser.parse_known_args()\n"
                "with open(os.environ['PKM_TEST_LOG'], 'a') as log:\n"
                "    log.write(json.dumps({'cwd': os.getcwd(), 'args': sys.argv[1:], 'vault_root': options.vault_root}) + '\\n')\n"
            )
            for name in ["pkm_quickadd.py"]:
                (vault / "scripts" / name).write_text(stub, encoding="utf-8")
                (workspace / name).write_text("raise SystemExit('wrong workspace')\n", encoding="utf-8")
            log = root / "calls.jsonl"
            examples = []
            for skill in sorted((REPOSITORY / "skills").glob("pkm-*")):
                for block in re.findall(r"```bash\n(.*?)```", (skill / "SKILL.md").read_text(), re.S):
                    if "pkm_quickadd.py" in block:
                        examples.append((skill.name, block))
            self.assertTrue(examples)
            for name, block in examples:
                for value in [None, "", ".", str(root / "missing"), str(vault)]:
                    with self.subTest(skill=name, value=value, command=block):
                        log.unlink(missing_ok=True)
                        environment = os.environ.copy()
                        environment.pop("PKM_VALUT_DIR", None)
                        environment["PKM_TEST_LOG"] = str(log)
                        environment["PKM_VAULT"] = str(workspace)
                        if value is not None:
                            environment["PKM_VALUT_DIR"] = value
                        result = subprocess.run(
                            ["bash", "-c", block], cwd=workspace, env=environment,
                            capture_output=True, text=True,
                        )
                        if value != str(vault):
                            self.assertNotEqual(result.returncode, 0)
                            self.assertFalse(log.exists())
                            continue
                        self.assertEqual(result.returncode, 0, result.stderr)
                        calls = [json.loads(line) for line in log.read_text().splitlines()]
                        self.assertTrue(calls)
                        for call in calls:
                            self.assertEqual(call["cwd"], str(vault))
                            self.assertEqual(call["vault_root"], str(vault))
                            if "--vault-root" in call["args"]:
                                index = call["args"].index("--vault-root")
                                self.assertEqual(call["args"][index + 1], str(vault))


if __name__ == "__main__":
    unittest.main()
