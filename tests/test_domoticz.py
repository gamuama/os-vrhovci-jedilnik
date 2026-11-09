import sys, unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from vrhovci_jedilnik.domoticz import next_school_date, format_day
class TestDomoticz(unittest.TestCase):
    def test_friday_to_monday(self): self.assertEqual(next_school_date(date(2026,11,13)),date(2026,11,16))
    def test_format(self):
        self.assertEqual(format_day({"dop_malica":"A","kosilo":"B","pop_malica":"C"},{},"X"),"Dop. malica: A\nKosilo: B\nPop. malica: C")
