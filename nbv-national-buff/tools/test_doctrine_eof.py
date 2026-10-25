"""Check the exact-file recovery for the shipped final submarine doctrine.

Run: python tools/test_doctrine_eof.py
The tests never write installed game definitions.
"""
import hashlib
import unittest
from unittest.mock import patch

import build_doctrine_technology_source_bindings as source


class DoctrineEofRecoveryTests(unittest.TestCase):
    fixture = ("wolfpacks = { naval_retreat_speed_after_initial_combat = 0.15 }\n"
               "long_range_submarines = {\n"
               " naval_torpedo_hit_chance_factor = 0.1\n"
               " rewards = { example = { submarine = { torpedo_attack = 0.1 } } }\n")

    @staticmethod
    def digest(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def recover(self, text, approved=None, filename=None):
        approved_sha = self.digest(approved if approved is not None else text)
        with patch.object(source, "VERIFIED_SUBMARINE_EOF_SHA256", approved_sha):
            return source.parse_doctrine_file(
                text, filename or source.VERIFIED_SUBMARINE_EOF_FILE, self.digest(text))

    def test_only_final_definition_closes_and_earlier_doctrine_survives(self):
        tree, recovery = self.recover(self.fixture)
        self.assertEqual([node.key for node in tree], ["wolfpacks", "long_range_submarines"])
        self.assertEqual(source.scalar(tree[0].value, "naval_retreat_speed_after_initial_combat"), "0.15")
        self.assertEqual(source.scalar(tree[1].value, "naval_torpedo_hit_chance_factor"), "0.1")
        self.assertEqual(recovery["appended_closing_braces"], 1)
        self.assertFalse(recovery["source_files_modified"])

    def test_complete_file_uses_strict_parse(self):
        tree, recovery = self.recover(self.fixture + "}\n")
        self.assertEqual(len(tree), 2)
        self.assertIsNone(recovery)

    def test_unknown_filename_and_changed_bytes_are_rejected(self):
        with self.assertRaises(source.ParseError):
            self.recover(self.fixture, filename="common/doctrines/subdoctrines/other.txt")
        with self.assertRaises(source.ParseError):
            self.recover(self.fixture + "# changed\n", approved=self.fixture)

    def test_other_unclosed_definition_and_nested_omission_are_rejected(self):
        for text in ("another_doctrine = { value = 1",
                     "long_range_submarines = { rewards = { sample = {}"):
            with self.subTest(text=text), self.assertRaises(source.ParseError):
                self.recover(text)

    def test_other_syntax_errors_are_rejected(self):
        for text in ("long_range_submarines = { value = }",
                     "long_range_submarines = {} }", "long_range_submarines > {"):
            with self.subTest(text=text), self.assertRaises(source.ParseError):
                self.recover(text)


if __name__ == "__main__":
    unittest.main()
