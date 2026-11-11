"""Retrieve a player's profile and career match data from Tennis Abstract."""

from datetime import date, datetime
from functools import lru_cache
from html import unescape
import re
from time import sleep
import unicodedata
from urllib.parse import parse_qs, urlsplit

import pandas as pd
import requests

from ._career import _parse_career_matches


_SITE = "https://www.tennisabstract.com"
_BIRTH_DATE = re.compile(r"\bvar\s+dob\s*=\s*['\"]?([0-9]{8})\b")
_PROFILE_NAME = re.compile(r"<title[^>]*>\s*Tennis Abstract:\s*(.+?)\s+Match Results", re.I | re.S)


def _request_with_retry(url: str, params: dict[str, str]) -> requests.Response:
    response = requests.get(url, params=params or None, timeout=15)
    if response.status_code == 429:
        delay = response.headers.get("Retry-After", "5")
        if re.fullmatch(r"[0-9]{1,2}", delay) and int(delay) <= 10:
            sleep(max(1, int(delay)))
            response = requests.get(url, params=params or None, timeout=15)
    return response


def _get(path: str, **params: str) -> requests.Response | None:
    try:
        response = _request_with_retry(_SITE + path, params)
        if response.status_code == 404:
            return None
        response.raise_for_status()
    except requests.RequestException as error:
        raise ConnectionError(f"Tennis Abstract request failed: {error}") from error
    return response


def _name_parts(name: str) -> list[str]:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.findall(r"[A-Za-z0-9]+", ascii_name)


def _guess_player_id(name: str) -> str:
    return "".join(
        part.capitalize() if part.islower() or part.isupper() else part
        for part in _name_parts(name)
    )


def _lookup_player_id(name: str, guessed_id: str) -> str | None:
    response = _get("/cgi-bin/search.cgi", q=name)
    results = response.json() if response is not None else []
    for result in results:
        if "".join(_name_parts(result["name"])).lower() == guessed_id.lower():
            profile_query = parse_qs(urlsplit(result["url"]).query)
            player_id = profile_query.get("p", [""])[0].rsplit("/", 1)[-1]
            if re.fullmatch(r"[A-Za-z0-9]+", player_id):
                return player_id
    return None


@lru_cache(maxsize=128)
def _player_profile(player_id: str) -> tuple[date, str | None]:
    response = _get("/cgi-bin/player.cgi", p=player_id)
    birth_date = _BIRTH_DATE.search(response.text) if response is not None else None
    if birth_date is None:
        raise ValueError(f"Birth date unavailable in the Tennis Abstract profile for {player_id}.")
    name = _PROFILE_NAME.search(response.text)
    display_name = unescape(name.group(1).strip()) if name else None
    return datetime.strptime(birth_date.group(1), "%Y%m%d").date(), display_name


def get_player_matches(player_name: str) -> pd.DataFrame:
    """Return career matches with player age, opponent age, and win or loss."""
    if not isinstance(player_name, str):
        raise TypeError("player_name must be a string.")
    player_id = _guess_player_id(player_name)
    if not player_id:
        raise ValueError("Enter a tennis player's name.")
    career = _get(f"/jsmatches/{player_id}Career.js")
    if career is None:
        listed_id = _lookup_player_id(player_name.strip(), player_id)
        if listed_id is not None and listed_id != player_id:
            player_id = listed_id
            career = _get(f"/jsmatches/{player_id}Career.js")
    if career is None:
        raise ValueError(f"Player not found on Tennis Abstract: {player_name.strip()!r}.")
    birth_date, display_name = _player_profile(player_id)
    matches = _parse_career_matches(career.content.decode("utf-8-sig"), birth_date)
    matches.attrs["player_name"] = display_name or player_name.strip()
    return matches
