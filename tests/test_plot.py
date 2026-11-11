import unittest

from matplotlib.colors import to_rgba
import matplotlib.pyplot as plt
import pandas as pd

from tennis_career import plot_age_gap


class AgeGapPlotTests(unittest.TestCase):
    def test_plot_uses_ages_and_colors_for_each_result(self):
        matches = pd.DataFrame({
            "player_age": [20, 21, 22],
            "age_difference": [-2, 3, float("nan")],
            "result": ["W", "L", "W"],
        })
        matches.attrs["player_name"] = "Example Player"
        axes = plot_age_gap(matches)
        self.addCleanup(plt.close, axes.figure)
        wins, losses = axes.collections
        self.assertEqual(wins.get_offsets().tolist(), [[20, -2]])
        self.assertEqual(losses.get_offsets().tolist(), [[21, 3]])
        self.assertEqual(tuple(wins.get_facecolors()[0]), to_rgba("#40C9E8", alpha=0.8))
        self.assertEqual(tuple(losses.get_facecolors()[0]), to_rgba("#96358F", alpha=0.8))
        self.assertEqual(axes.get_title(), "Example Player")
        self.assertEqual(list(axes.texts), [])

    def test_plot_reports_missing_columns(self):
        with self.assertRaisesRegex(ValueError, "Missing match columns.*age_difference"):
            plot_age_gap(pd.DataFrame({"player_age": [20], "result": ["W"]}))
