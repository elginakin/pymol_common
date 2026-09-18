"""Regression tests for the configuration-driven 4FQM figure generator."""

from __future__ import annotations

import unittest
import sys
from pathlib import Path


STRUCTURE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from pymol_common import structure_workflow as generator  # noqa: E402


class NumberingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = generator.load_json(STRUCTURE_ROOT / "config" / "base.json")
        cls.numbering = cls.base["numbering"]

    def test_sequential_to_author_numbering(self) -> None:
        expected = {
            163: "163",
            164: "163A",
            165: "163B",
            166: "163C",
            167: "164",
            197: "194",
            199: "196",
            208: "205",
        }
        observed = {
            position: generator.sequential_to_author(position, self.numbering)
            for position in expected
        }
        self.assertEqual(observed, expected)


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = generator.load_json(STRUCTURE_ROOT / "config" / "base.json")
        cls.profiles = generator.load_json(STRUCTURE_ROOT / "config" / "profiles.json")[
            "profiles"
        ]

    def profile(self, name: str) -> dict:
        return next(profile for profile in self.profiles if profile["name"] == name)

    def test_example_profile_mutations(self) -> None:
        profile = self.profile("C.3.1")
        config = generator.apply_overrides(self.base, profile, [], [])
        pml, author_ids = generator.build_pml(
            config, profile, "outputs/figures", "outputs/sessions", True
        )
        self.assertEqual(author_ids, ["194", "205"])
        self.assertIn("select mutation_197, focus_ha1 and resi 194", pml)
        self.assertIn("select mutation_208, focus_ha1 and resi 205", pml)

    def test_glycan_and_antigenic_cli_toggles(self) -> None:
        profile = self.profile("C.3.1")
        config = generator.apply_overrides(
            self.base,
            profile,
            [("HA1_N197", False)],
            [("160_loop", False)],
        )
        pml, _ = generator.build_pml(
            config, profile, "outputs/figures", "outputs/sessions", True
        )
        focus_glycan_line = next(
            line for line in pml.splitlines() if line.startswith("select focus_glycans,")
        )
        antigenic_line = next(
            line for line in pml.splitlines() if line.startswith("select antigenic_sites,")
        )
        self.assertNotIn("glycan_HA1_N197", focus_glycan_line)
        self.assertNotIn("antigenic_160_loop", antigenic_line)
        self.assertIn("select emphasized_glycans, none", pml)


if __name__ == "__main__":
    unittest.main()
