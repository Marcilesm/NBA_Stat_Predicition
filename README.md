# 🏀 NBA Player Performance Prediction

This project estimates an NBA player's performance for a given matchup using historical data, weighted statistics, and team defensive profiles.

> This project is no longer actively maintained. It remains available for review as a portfolio piece.

A data-driven tool for generating predicted NBA player stat lines based on:
- Career averages
- Current season performance
- Opponent-specific matchups
- Team defensive metrics

---

## Features

- Predict key box score stats:
  - Points, Assists, Rebounds, Steals, Blocks
  - Turnovers, Free Throw Attempts, 3PA, Minutes
- Blended model using:
  - Career averages
  - Season averages
  - Matchup-specific stats
  - Opponent team defensive metrics
- Accuracy checker against most recent game
- Fully scriptable — no GUI needed

---

## Project Structure

```
NBA_Player_Performance/
├── data/
│   ├── cleaned_game_logs_2023.csv
│   ├── player_career_averages.csv
│   └── opponent_team_defense.csv
├── team_stats.py
├── weighted_model.py
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Set up your environment

```bash
python -m venv venv
venv\Scripts\activate         # On Windows
# Or use `source venv/bin/activate` on macOS/Linux

pip install -r requirements.txt
```

### 2. Run a prediction

```bash
python weighted_model.py
```

You'll be prompted to enter:
- Player name (e.g., `lebron james`)
- Opponent abbreviation (e.g., `DET`)
- Home game? (`y` or `n`)

The model outputs the blended prediction and compares it against the most recent actual game data.

---

## How It Works

Each stat is computed using weighted contributions:

- `w_career` = 0.3 (long-term performance)
- `w_season` = 0.5 (recent form)
- `w_matchup` = 0.2 (vs opponent)
- Certain features (like REB, FTA) are adjusted further using team defense stats:
  - `OREB_ALLOWED`, `FTA_ALLOWED`, etc.

Example:
```text
PTS      | Predicted: 26.22 | Actual: 25.00 | Error: 4.88%
REB      | Predicted: 6.12  | Actual: 1.00  | Error: 511.74%
```

---

## Requirements

- `pandas`
- `numpy`
- `nba_api`

Install them via:

```bash
pip install -r requirements.txt
```

---

## License

This project is licensed under the MIT License.

---

