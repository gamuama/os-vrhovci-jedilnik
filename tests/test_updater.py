import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vrhovci_jedilnik.updater import target_week_bounds, existing_json_has_target_week, find_pdf_for_target_week


class UpdaterTest(unittest.TestCase):
    def test_weekday_uses_current_week(self):
        self.assertEqual(target_week_bounds(date(2026, 11, 9)), (date(2026, 11, 9), date(2026, 11, 13)))

    def test_saturday_uses_next_week(self):
        self.assertEqual(target_week_bounds(date(2026, 11, 14)), (date(2026, 11, 16), date(2026, 11, 20)))

    def test_sunday_uses_next_week(self):
        self.assertEqual(target_week_bounds(date(2026, 11, 15)), (date(2026, 11, 16), date(2026, 11, 20)))

    def test_existing_current_json_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "jedilnik.json"
            p.write_text(json.dumps({
                "week_from": "2026-11-09", "week_to": "2026-11-13",
                "days": {str(i): {} for i in range(5)}
            }), encoding="utf-8")
            self.assertTrue(existing_json_has_target_week(p, date(2026, 11, 9)))
            self.assertFalse(existing_json_has_target_week(p, date(2026, 11, 14)))

    def test_find_target_pdf(self):
        html = '''<table><tr><td>2. teden</td><td><a href="/files/2.pdf">09. - 13.</a></td></tr>
        <tr><td>3. teden</td><td><a href="/files/3.pdf">16. - 20.</a></td></tr></table>'''
        self.assertEqual(
            find_pdf_for_target_week(html, "https://example.test/jedilniki/", date(2026, 11, 9)),
            "https://example.test/files/2.pdf",
        )

if __name__ == "__main__":
    unittest.main()
