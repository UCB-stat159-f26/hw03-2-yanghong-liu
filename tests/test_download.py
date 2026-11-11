from pathlib import Path
import unittest
from unittest.mock import patch

import requests

from tennis_career import get_player_matches


FIXTURES = Path(__file__).parent / "fixtures"
SERENA_PROFILE = """
<title>Tennis Abstract: Serena Williams Match Results, Splits, and Analysis</title>
<script>var dob = 19810926;</script>
"""


def _response(body: str, status: int = 200) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response.encoding = "utf-8"
    response._content = body.encode("utf-8")
    return response


class PlayerDownloadTests(unittest.TestCase):
    @patch("tennis_career._download.requests.get")
    def test_serena_name_formats_resolve_to_the_same_player(self, request):
        career = (FIXTURES / "serena_career.js").read_text(encoding="utf-8")
        for name in ("serena williams", "Serena Williams", "SerenaWilliams"):
            with self.subTest(name=name):
                request.reset_mock()
                request.side_effect = [_response(career), _response(SERENA_PROFILE)]
                matches = get_player_matches(name)
                self.assertEqual(matches.attrs["player_name"], "Serena Williams")
                self.assertEqual(matches["opponent"].tolist(), ["Anne Miller"])
                first_url = request.call_args_list[0].args[0]
                self.assertTrue(first_url.endswith("/SerenaWilliamsCareer.js"))

    @patch("tennis_career._download.requests.get")
    def test_search_resolves_the_canonical_id(self, request):
        career = (FIXTURES / "nadal_career.js").read_text(encoding="utf-8")
        search = '[{"name":"John McEnroe","url":"/cgi-bin/player.cgi?p=123/JohnMcEnroe"}]'
        profile = SERENA_PROFILE.replace("Serena Williams", "John McEnroe")
        request.side_effect = [_response("", 404), _response(search), _response(career), _response(profile)]
        matches = get_player_matches("john mcenroe")
        self.assertEqual(matches.attrs["player_name"], "John McEnroe")
        self.assertTrue(request.call_args_list[2].args[0].endswith("/JohnMcEnroeCareer.js"))

    @patch("tennis_career._download.requests.get")
    def test_unknown_player_error_names_the_input(self, request):
        request.side_effect = [_response("", 404), _response("[]")]
        with self.assertRaisesRegex(ValueError, "Player not found.*Gaston Sanchez"):
            get_player_matches("Gaston Sanchez")

    @patch("tennis_career._download.requests.get", side_effect=requests.Timeout("Test timeout"))
    def test_timeout_is_reported_as_a_connection_error(self, request):
        with self.assertRaisesRegex(ConnectionError, "Tennis Abstract request failed"):
            get_player_matches("Serena Williams")
