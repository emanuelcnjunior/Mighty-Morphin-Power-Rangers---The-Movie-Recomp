"""Unit tests for SNES Game Genie and Pro Action Replay parsing and decoding."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cheat_tool


class TestCheatTool(unittest.TestCase):
    def test_snes_game_genie_decoding(self):
        # Known test vectors for SNES:
        # DB6E-0D6D: Start with 9 lives in MMPR Movie -> ROM address 0x0081F2, value 0x09
        p1 = cheat_tool.decode_game_genie("DB6E-0D6D")
        self.assertEqual(p1.kind, "rom")
        self.assertEqual(p1.address, 0x0081F2)
        self.assertEqual(p1.value, 0x09)

        # D96E-0D6D: Start with 5 lives -> ROM address 0x0081F2, value 0x05
        p2 = cheat_tool.decode_game_genie("D96E-0D6D")
        self.assertEqual(p2.address, 0x0081F2)
        self.assertEqual(p2.value, 0x05)

        # 8B26-07A2: Almost infinite life force -> ROM address 0x03D58F, value 0xB9
        p3 = cheat_tool.decode_game_genie("8B26-07A2")
        self.assertEqual(p3.address, 0x03D58F)
        self.assertEqual(p3.value, 0xB9)

    def test_pro_action_replay_decoding(self):
        # 7E0628:05 -> RAM address 0x7E0628, value 0x05
        p1 = cheat_tool.decode_pro_action_replay("7E0628:05")
        self.assertEqual(p1.kind, "ram")
        self.assertEqual(p1.address, 0x7E0628)
        self.assertEqual(p1.value, 0x05)

        # Without colon: 7E062A18 -> RAM address 0x7E062A, value 0x18
        p2 = cheat_tool.decode_pro_action_replay("7E062A18")
        self.assertEqual(p2.kind, "ram")
        self.assertEqual(p2.address, 0x7E062A)
        self.assertEqual(p2.value, 0x18)

        # 049D34:AD -> ROM address 0x049D34, value 0xAD
        p3 = cheat_tool.decode_pro_action_replay("049D34:AD")
        self.assertEqual(p3.kind, "rom")
        self.assertEqual(p3.address, 0x049D34)
        self.assertEqual(p3.value, 0xAD)

    def test_invalid_cheat_codes(self):
        with self.assertRaisesRegex(ValueError, "Invalid SNES Game Genie format"):
            cheat_tool.decode_game_genie("SHORT")

        with self.assertRaisesRegex(ValueError, "Invalid character"):
            cheat_tool.decode_game_genie("ZZZZ-ZZZZ")

        with self.assertRaisesRegex(ValueError, "Invalid SNES Pro Action Replay"):
            cheat_tool.decode_pro_action_replay("12345")

    def test_parse_catalog(self):
        cht_path = ROOT / "config/power_rangers_the_movie_usa.cht"
        cheats = cheat_tool.parse(cht_path)
        self.assertEqual(len(cheats), 40)
        self.assertTrue(all(not c.enabled for c in cheats))

        # Check multi-part cheat 21
        multi = cheats[21]
        self.assertEqual(len(multi.patches), 2)
        self.assertIn("+", multi.code)

    def test_select_and_conflict_rejection(self):
        cht_path = ROOT / "config/power_rangers_the_movie_usa.cht"
        cheats = cheat_tool.parse(cht_path)

        # Non-conflicting selection
        selected = cheat_tool.select(cheats, "0, 1, 2, 15")
        self.assertEqual([c.index for c in selected], [0, 1, 2, 15])

        # Conflicting selection: cheat 15 (9 lives) and cheat 16 (5 lives) both write to 0x0081F2
        with self.assertRaisesRegex(ValueError, "Conflict"):
            cheat_tool.select(cheats, "15, 16")


if __name__ == "__main__":
    unittest.main()
