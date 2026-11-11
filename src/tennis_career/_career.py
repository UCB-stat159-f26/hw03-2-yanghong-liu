"""Read match records and calculate the ages used in career plots."""

from datetime import date
import json
import re

import pandas as pd


_MATCH_ARRAY = re.compile(r"\bvar\s+morematchmx\s*=\s*")
_MATCH_FIELDS = {
    "match_date": 0,
    "result": 4,
    "opponent": 11,
    "opponent_age_value": 16,
}


def _read_match_rows(source: str) -> list[list[str]]:
    """Read the JSON array inside a Tennis Abstract career file."""
    assignment = _MATCH_ARRAY.search(source)
    if assignment is None:
        raise ValueError("No career match array found in the Tennis Abstract response.")
    rows, _ = json.JSONDecoder().raw_decode(source[assignment.end():])
    if not isinstance(rows, list) or not rows:
        raise ValueError("The career match array is empty or invalid.")
    return rows


def _match_fields(row: list[str]) -> dict[str, str]:
    if not isinstance(row, list) or len(row) <= max(_MATCH_FIELDS.values()):
        raise ValueError("A career match row is missing required fields.")
    return {name: row[index] for name, index in _MATCH_FIELDS.items()}


def _age_in_years(match_dates: pd.Series, birth_dates: pd.Series | pd.Timestamp) -> pd.Series:
    return (match_dates - birth_dates).dt.days / 365.25


def _opponent_ages(values: pd.Series, match_dates: pd.Series) -> pd.Series:
    """Interpret the field as a birth date or an age already in years."""
    values = values.astype("string").str.strip()
    is_birth_date = values.str.fullmatch(r"[0-9]{8}", na=False)
    birth_dates = pd.to_datetime(values.where(is_birth_date), format="%Y%m%d", errors="coerce")
    listed_ages = pd.to_numeric(values.mask(is_birth_date), errors="coerce").astype(float)
    ages = listed_ages.mask(is_birth_date, _age_in_years(match_dates, birth_dates))
    return ages.where(ages > 0)


def _parse_career_matches(source: str, player_birth_date: date) -> pd.DataFrame:
    """Convert career match rows to ages and results."""
    matches = pd.DataFrame.from_records(map(_match_fields, _read_match_rows(source)))
    match_dates = pd.to_datetime(matches["match_date"], format="%Y%m%d")
    opponent_age_values = matches.pop("opponent_age_value")
    matches["match_date"] = match_dates
    matches["player_age"] = _age_in_years(match_dates, pd.Timestamp(player_birth_date))
    matches["opponent_age"] = _opponent_ages(opponent_age_values, match_dates)
    matches["age_difference"] = matches["player_age"] - matches["opponent_age"]
    return matches
