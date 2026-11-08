import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vrhovci_jedilnik.parser import parse_menu


class ParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = Path(__file__).parent / "fixtures" / "menu.txt"
        cls.result = parse_menu(fixture.read_text(encoding="utf-8"))

    def test_week(self):
        self.assertEqual(self.result["week_from"], "2026-11-09")
        self.assertEqual(self.result["week_to"], "2026-11-13")

    def test_all_five_days(self):
        self.assertEqual(len(self.result["days"]), 5)

    def test_monday(self):
        monday = self.result["days"]["ponedeljek"]
        self.assertEqual(monday["date"], "2026-11-09")
        self.assertIn("BIO pecivo", monday["dop_malica"])
        self.assertIn("lazanja", monday["kosilo"])
        self.assertEqual(monday["pop_malica"], "Riževi vaflji, pomaranča")

    def test_friday_notes_are_excluded(self):
        value = self.result["days"]["petek"]["pop_malica"]
        self.assertEqual(value, "Sadni jogurt (7), prepečenec (1)")
        self.assertNotIn("Opombe", value)


if __name__ == "__main__":
    unittest.main()
