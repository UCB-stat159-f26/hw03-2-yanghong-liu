# Tennis Career

Python package for STAT 159/259 HW 03. The package will retrieve a player's career matches from Tennis Abstract and plot their age against the age difference with each opponent.

## Local installation

From the repository root, run:

```sh
python -m pip install .
python -c "import tennis_career"
```

## Tests

Run `python -m unittest discover -s tests` from the repository root. The Serena fixture is a small example based on the match data in the [HW 03 instructions](https://stat159.berkeley.edu/fall-2026/hws/hw03/hw03.html#tests).

## AI assistance

I used OpenAI Codex (GPT-6) to review the HW 03 requirements, set up the package, and adapt the HW 02 parser and age calculations for offline testing. The main prompts were “这个作业怎么写” and “好的我们现在开始看HW3要怎么做”. This assistance covered the package layout, `pyproject.toml`, `_career.py`, the Serena fixture tests, and the installation check.
