"""Unit tests for the RecompLauncher profile and game default settings synchronization."""
import codecs
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestLauncherProfile(unittest.TestCase):
    def test_recomplauncher_profile_structure(self):
        profile_path = ROOT / "recomplauncher.json"
        self.assertTrue(profile_path.is_file(), "recomplauncher.json must exist")

        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        self.assertEqual(profile.get("format"), 1)
        self.assertIn("Power Rangers", profile.get("name", ""))
        self.assertEqual(profile.get("repo"), "emanuelcnjunior/Mighty-Morphin-Power-Rangers---The-Movie-Recomp")

        # Inputs
        self.assertIn("inputs", profile)
        self.assertEqual(profile["inputs"][0]["id"], "rom")

        # Prepare (ROM import)
        self.assertIn("prepare", profile)
        self.assertIn("--import-rom", profile["prepare"]["args"])

        # Start
        self.assertIn("start", profile)
        self.assertIn("--no-launcher", profile["start"]["args"])

        # Settings
        self.assertIn("settings", profile)
        setting_ids = [s["id"] for s in profile["settings"]]
        self.assertIn("vsync", setting_ids)
        self.assertIn("audio", setting_ids)
        self.assertIn("volume", setting_ids)

    def test_first_run_defaults_match_game_source(self):
        profile = json.loads((ROOT / "recomplauncher.json").read_text(encoding="utf-8"))
        profile_defaults = profile["config"][0]["new"]

        source = (ROOT / "src/game_paths.c").read_text(encoding="utf-8")
        source = source.split("const char kGameDefaultConfig[] =", 1)[1].split(";", 1)[0]
        ini = "".join(codecs.decode(s, "unicode_escape") for s in re.findall(r'"([^"]*)"', source))

        game_defaults = {}
        section = ""
        for line in ini.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
            elif "=" in line:
                key, val = line.split("=", 1)
                game_defaults[f"{section}/{key.strip()}"] = val.strip()

        self.assertEqual(profile_defaults, game_defaults, "recomplauncher.json defaults must match game_paths.c")


if __name__ == "__main__":
    unittest.main()
