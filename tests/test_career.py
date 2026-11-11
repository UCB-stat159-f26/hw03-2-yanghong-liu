from datetime import date
from pathlib import Path
import unittest

from tennis_career._career import _parse_career_matches


FIXTURES = Path(__file__).parent / "fixtures"
SERENA_BIRTH_DATE = date(1981, 9, 26)
NADAL_BIRTH_DATE = date(1986, 6, 3)


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

    def test_nadal_fixture_keeps_opponent_age_in_years(self):
        source = (FIXTURES / "nadal_career.js").read_text(encoding="utf-8")
        first = _parse_career_matches(source, NADAL_BIRTH_DATE).iloc[0]
        self.assertEqual(first["opponent"], "Guillermo Platel")
        self.assertEqual(first["result"], "L")
        self.assertAlmostEqual(first["player_age"], 15.27173169062286)
        self.assertAlmostEqual(first["opponent_age"], 22.264202601)
        self.assertAlmostEqual(first["age_difference"], -6.99247091037714)

    def test_missing_opponent_age_keeps_the_match(self):
        source = (FIXTURES / "nadal_career.js").read_text(encoding="utf-8")
        matches = _parse_career_matches(source.replace("22.264202601", ""), NADAL_BIRTH_DATE)
        self.assertEqual(matches["opponent"].tolist(), ["Guillermo Platel"])
        self.assertTrue(matches["opponent_age"].isna().all())
        self.assertTrue(matches["age_difference"].isna().all())

    def test_missing_match_array_reports_a_clear_error(self):
        with self.assertRaisesRegex(ValueError, "No career match array"):
            _parse_career_matches("var other_data = [];", SERENA_BIRTH_DATE)
