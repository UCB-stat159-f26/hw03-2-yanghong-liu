# Tennis Career

Python package for STAT 159/259 HW 03. It retrieves career match records from
[Tennis Abstract](https://www.tennisabstract.com/) and plots age differences by match result.

## Installation

With Python 3.10 or newer and access to the course repository, run the following command.

```sh
python -m pip install "git+https://github.com/UCB-stat159-f26/hw03-2-yanghong-liu.git"
```

If you already cloned the repository, run `python -m pip install .` in its root directory.

## Usage

```python
from tennis_career import get_player_matches, plot_age_gap

serena = get_player_matches("serena williams")
nadal = get_player_matches("Rafael Nadal")

plot_age_gap(serena).figure.savefig("serena-age-gap.png", dpi=150)
plot_age_gap(nadal).figure.savefig("nadal-age-gap.png", dpi=150)
```

`get_player_matches` also accepts names such as `"Serena Williams"` and
`"SerenaWilliams"`. An unknown player such as `"GastonSanchez"` raises a
`ValueError` that names the input.

The returned DataFrame has `match_date`, `result`, `opponent`, `player_age`,
`opponent_age`, and `age_difference` columns. Dates are tournament dates
from the source. For fields supplied as birth dates, ages are elapsed days
divided by 365.25. Opponent ages supplied in years are used directly.
The age difference is the player's age minus the opponent's age.

`plot_age_gap` returns a Matplotlib `Axes`. The x-axis shows the player's
age and the y-axis shows the age difference. Cyan dots mark wins and purple
dots mark losses. Matches with missing opponent ages stay in the DataFrame.
The scatter plot uses wins and losses with both ages available.

## Tests

Run the tests from the repository root after installation.

```sh
MPLBACKEND=Agg python -m unittest discover -s tests -v
```

The tests run offline. The Serena and Nadal fixtures use the two formats
in the [HW 03 instructions](https://stat159.berkeley.edu/fall-2026/hws/hw03/hw03.html#tests).
The tests check the calculated ages, simulate download responses, and verify
the coordinates and colors of the scatter plot.

## Personal reflections

My HW 02 feedback pointed out that I had put too much work in one commit.
The HW 03 history makes it easier to see when the Serena parser worked
and when support for Nadal's data was added. I want to keep using passing
tests as checkpoints for individual commits in future projects.

The two fixtures show why those checkpoints matter. Serena's file lists
Anne Miller's birth date, while Nadal's file already lists Guillermo
Platel's age in years. A small offline test for each format lets me verify
the age difference independently of the website.

## AI assistance

I used OpenAI Codex (GPT-6) to review the requirements, draft the package,
tests, and README, and verify the installation and examples. The main
prompts were “这个作业怎么写” and “结合作业要求和我们之前的HW2老师给的反馈，你觉得这一次的HW3怎么做可以满分”.
