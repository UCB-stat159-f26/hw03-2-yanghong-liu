from datetime import date
from pathlib import Path
import unittest

from tennis_career._career import _parse_career_matches


FIXTURES = Path(__file__).parent / "fixtures"
SERENA_BIRTH_DATE = date(1981, 9, 26)


class CareerMatchTests(unittest.TestCase):
    def test_serena_match_from_local_fixture(self):
        source = (FIXTURES / "serena_career.js").read_text(encoding="utf-8")
        matches = _parse_career_matches(source, SERENA_BIRTH_DATE)
        self.assertEqual(len(matches), 1)
        first = matches.iloc[0]
        self.assertEqual(first["match_date"].date(), date(1995, 10, 30))
        self.assertEqual(first["opponent"], "Anne Miller")
        self.assertEqual(first["result"], "L")
        self.assertAlmostEqual(first["player_age"], 14.091718001368925)
        self.assertAlmostEqual(first["opponent_age"], 18.77618069815195)
        self.assertAlmostEqual(first["age_difference"], -4.684462696783027)

    def test_missing_match_array_reports_a_clear_error(self):
        with self.assertRaisesRegex(ValueError, "No career match array"):
            _parse_career_matches("var other_data = [];", SERENA_BIRTH_DATE)
