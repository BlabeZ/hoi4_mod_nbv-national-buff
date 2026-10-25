"""Regressions for source loss caused by vanilla idea-file EOF wrappers.

Run: python tools/test_idea_sources.py
Tests use small fixtures; no installed game files are written.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_source_bindings as source


class IdeaSourceRecoveryTests(unittest.TestCase):
    filename = "common/ideas/SOV.txt"
    fixture = """ideas = {
 country = {
  trotskyite_plot_nsb = {
   name = trotskyite_plot
   allowed = { always = no }
   modifier = { stability_factor = -0.2 political_power_factor = -0.15 }
  }
  SOV_politicized_military = {
   modifier = { army_core_defence_factor = 0.03 command_abilities_cost_factor = 0.1 }
  }
 }
"""

    @staticmethod
    def digest(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def recover(self, text, approved=None, filename=None):
        sha = self.digest(text)
        allowlist = {self.filename: self.digest(approved if approved is not None else text)}
        with patch.dict(source.VERIFIED_OUTER_IDEAS_EOF, allowlist, clear=True):
            return source.parse_idea_file(text, filename or self.filename, sha)

    def test_exact_audited_outer_eof_recovers_and_reports(self):
        tree, recovery = self.recover(self.fixture)
        self.assertEqual(tree[0].key, "ideas")
        self.assertEqual([idea.key for idea in tree[0].value[0].value],
                         ["trotskyite_plot_nsb", "SOV_politicized_military"])
        self.assertEqual(recovery["appended_closing_braces"], 1)
        self.assertFalse(recovery["source_files_modified"])

    def test_correctly_closed_file_stays_strict_and_unmodified(self):
        tree, recovery = self.recover(self.fixture + "}\n")
        self.assertEqual(tree[0].key, "ideas")
        self.assertIsNone(recovery)

    def test_unknown_file_and_changed_content_fail_closed(self):
        with self.assertRaises(source.ParseError):
            self.recover(self.fixture, filename="common/ideas/third_party.txt")
        with self.assertRaises(source.ParseError):
            self.recover(self.fixture + "# changed\n", approved=self.fixture)

    def test_unclosed_inner_block_is_not_repaired(self):
        # Even with a test-approved hash, two unmatched wrappers are refused.
        with self.assertRaises(source.ParseError):
            self.recover("ideas = { country = { test = { modifier = {} }")

    def test_other_syntax_errors_are_not_repaired(self):
        for text in ("ideas = { country = { test = { modifier = } }",
                     "ideas = { country = {} }}", "other = { country = {}"):
            with self.subTest(text=text), self.assertRaises(source.ParseError):
                self.recover(text)

    def test_recovered_ideas_reach_bindings_without_changing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            game = Path(directory)
            idea = game / self.filename
            idea.parent.mkdir(parents=True)
            idea.write_text(self.fixture, encoding="utf-8")
            loc = game / "localisation/simp_chinese/fixture.yml"
            loc.parent.mkdir(parents=True)
            loc.write_text('l_simp_chinese:\n trotskyite_plot: "托洛茨基的阴谋？"\n'
                           ' SOV_politicized_military: "政治化的军队"\n', encoding="utf-8")
            index = game / "index.json"
            keys = {"stability_factor": -0.2, "political_power_factor": -0.15,
                    "army_core_defence_factor": 0.03, "command_abilities_cost_factor": 0.1}
            index.write_text(json.dumps({"records": [{"key": key} for key in keys]}),
                             encoding="utf-8")
            before = idea.read_bytes()
            with patch.dict(source.VERIFIED_OUTER_IDEAS_EOF,
                            {self.filename: source.digest(idea)}, clear=True):
                result = source.build(game, index)
            self.assertEqual(result["statistics"]["parse_failure_count"], 0)
            self.assertEqual(result["statistics"]["verified_eof_recovery_count"], 1)
            self.assertEqual(result["statistics"]["binding_count"], 4)
            for key, value in keys.items():
                binding, = result["by_modifier"][key]
                self.assertEqual(binding["value"], value)
                self.assertEqual(binding["activation_script"], f'has_idea = {binding["source_id"]}')
                self.assertNotIn("领袖", binding["name_zh"])
            self.assertEqual(idea.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
