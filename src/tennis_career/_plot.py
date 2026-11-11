"""Plot the age difference between a player and each opponent."""

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import pandas as pd


_OUTCOMES = {"W": ("Win", "#40C9E8"), "L": ("Loss", "#96358F")}


def _plot_data(matches: pd.DataFrame) -> pd.DataFrame:
    columns = ["player_age", "age_difference", "result"]
    missing = set(columns).difference(matches.columns)
    if missing:
        raise ValueError(f"Missing match columns: {', '.join(sorted(missing))}.")
    data = matches.loc[matches["result"].isin(_OUTCOMES), columns]
    data = data.replace([float("-inf"), float("inf")], float("nan")).dropna()
    if data.empty:
        raise ValueError("No wins or losses have both ages available for plotting.")
    return data


def plot_age_gap(matches: pd.DataFrame) -> Axes:
    """Plot player age and age difference from get_player_matches."""
    data = _plot_data(matches)
    figure, axes = plt.subplots(figsize=(9, 5))
    axes.set_axisbelow(True)
    axes.grid(color="#e6e6e6")
    axes.axhline(0, color="#666666", linewidth=0.8, zorder=1)
    for result, (label, color) in _OUTCOMES.items():
        group = data.loc[data["result"] == result]
        axes.scatter(
            group["player_age"], group["age_difference"],
            s=20, alpha=0.8, color=color, edgecolors="none", label=label, zorder=2,
        )
    axes.set_xlabel("Player age (years)")
    axes.set_ylabel("Player age − opponent age (years)")
    axes.set_title(matches.attrs.get("player_name", "Career matches"))
    axes.legend(title="Match outcome")
    figure.tight_layout()
    return axes
